from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime, timezone
import uuid
from django.db import transaction

from .models import Booking, Seat

# Pricing multipliers
SEAT_CLASS_MULTIPLIER = {
    'economy': Decimal('1.00'),
    'premium': Decimal('1.25'),
    'business': Decimal('1.75'),
    'first': Decimal('2.50'),
}

AIRLINE_SERVICE_MULTIPLIER = {
    'basic': Decimal('1.00'),
    'comfort': Decimal('1.10'),
    'premium': Decimal('1.25'),
}

AGE_DISCOUNTS = {
    'child_max_age': 12,
    'child_discount': Decimal('0.50'),
    'senior_min_age': 65,
    'senior_discount': Decimal('0.80'),
}

INCLUDED_LUGGAGE_KG = Decimal('15.0')
EXTRA_LUGGAGE_RATE_PER_KG = Decimal('5.00')

def _round(d: Decimal):
    return d.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

def calculate_price(base_price: Decimal, seat_class: str, airline_service: str, departure_datetime, booking_datetime=None, passenger_age: int = 30, luggage_kg: Decimal = Decimal('0'), seat_extra: Decimal = Decimal('0')):
    if booking_datetime is None:
        booking_datetime = datetime.now(timezone.utc)

    price = Decimal(base_price)
    price *= SEAT_CLASS_MULTIPLIER.get(seat_class, Decimal('1.0'))
    price *= AIRLINE_SERVICE_MULTIPLIER.get(airline_service, Decimal('1.0'))
    price += Decimal(seat_extra)

    # luggage surcharge
    if luggage_kg > INCLUDED_LUGGAGE_KG:
        extra_weight = luggage_kg - INCLUDED_LUGGAGE_KG
        price += extra_weight * EXTRA_LUGGAGE_RATE_PER_KG

    # time-to-journey surcharge
    delta = departure_datetime - booking_datetime
    days = Decimal(delta.total_seconds()) / Decimal(86400)
    if days <= 3:
        price *= Decimal('1.50')
    elif days <= 7:
        price *= Decimal('1.25')
    elif days <= 30:
        price *= Decimal('1.05')

    # age discount
    if passenger_age <= AGE_DISCOUNTS['child_max_age']:
        price *= AGE_DISCOUNTS['child_discount']
    elif passenger_age >= AGE_DISCOUNTS['senior_min_age']:
        price *= AGE_DISCOUNTS['senior_discount']

    return _round(price)

def generate_pnr():
    return str(uuid.uuid4())[:8].upper()

def book_seat(flight, seat, user, passenger_name, passenger_age, luggage_kg):
    """
    Concurrency-safe booking with transaction.
    Returns booking instance or raises Exception if seat booked.
    """
    with transaction.atomic():
        seat = Seat.objects.select_for_update().get(pk=seat.id)
        if seat.is_booked:
            raise Exception("Seat already booked")
        seat.is_booked = True
        seat.save()

        price = calculate_price(
            base_price=flight.base_price,
            seat_class=seat.seat_class,
            airline_service=flight.airline.service_tier,
            departure_datetime=flight.departure,
            passenger_age=passenger_age,
            luggage_kg=luggage_kg,
            seat_extra=seat.extra_cost
        )

        booking = Booking.objects.create(
            user=user,
            flight=flight,
            seat=seat,
            passenger_name=passenger_name,
            passenger_age=passenger_age,
            luggage_kg=luggage_kg,
            price_paid=price,
            status=Booking.CONFIRMED,
            confirmation_code=generate_pnr()
        )
        return booking
