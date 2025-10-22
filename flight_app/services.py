from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime, timezone
import uuid

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


def calculate_price(
    base_price: Decimal,
    seat_class: str,
    airline_service: str,
    departure_datetime,
    booking_datetime=None,
    passenger_age: int = 30,
    luggage_kg: Decimal = Decimal('0'),
    seat_extra: Decimal = Decimal('0'),
):
    if booking_datetime is None:
        booking_datetime = datetime.now(timezone.utc)

    price = Decimal(base_price)
    price *= SEAT_CLASS_MULTIPLIER.get(seat_class, Decimal('1.0'))
    price *= AIRLINE_SERVICE_MULTIPLIER.get(airline_service, Decimal('1.0'))
    price += Decimal(seat_extra)

    extra_luggage = Decimal('0')
    if luggage_kg > INCLUDED_LUGGAGE_KG:
        extra_luggage = (luggage_kg - INCLUDED_LUGGAGE_KG) * EXTRA_LUGGAGE_RATE_PER_KG
        price += extra_luggage

    delta = departure_datetime - booking_datetime
    days = Decimal(delta.total_seconds()) / Decimal(86400)

    if days < 0:
        time_multiplier = Decimal('1.0')
    elif days <= 3:
        time_multiplier = Decimal('1.50')
    elif days <= 7:
        time_multiplier = Decimal('1.25')
    elif days <= 30:
        time_multiplier = Decimal('1.05')
    else:
        time_multiplier = Decimal('1.00')

    price *= time_multiplier

    if passenger_age <= AGE_DISCOUNTS['child_max_age']:
        price *= AGE_DISCOUNTS['child_discount']
    elif passenger_age >= AGE_DISCOUNTS['senior_min_age']:
        price *= AGE_DISCOUNTS['senior_discount']

    final_price = _round(price)
    breakdown = {
        'base_price': _round(Decimal(base_price)),
        'seat_class_multiplier': SEAT_CLASS_MULTIPLIER.get(seat_class, Decimal('1.0')),
        'airline_service_multiplier': AIRLINE_SERVICE_MULTIPLIER.get(airline_service, Decimal('1.0')),
        'seat_extra': _round(Decimal(seat_extra)),
        'extra_luggage': _round(extra_luggage),
        'time_multiplier': time_multiplier,
        'age_applied': 'child' if passenger_age <= AGE_DISCOUNTS['child_max_age'] else ('senior' if passenger_age >= AGE_DISCOUNTS['senior_min_age'] else 'none'),
        'final_price': final_price,
    }
    return final_price, breakdown


def book_seat_and_create_booking(
    user,
    flight,
    seat,
    passenger_name,
    passenger_age,
    luggage_kg,
    booking_datetime=None
):
    from .models import Booking
    from django.db import transaction

    if booking_datetime is None:
        booking_datetime = datetime.now(timezone.utc)

    if seat.is_booked:
        return None, "Seat already booked"

    final_price, breakdown = calculate_price(
        base_price=flight.base_price,
        seat_class=seat.seat_class,
        airline_service=flight.airline.service_tier,
        departure_datetime=flight.departure,
        booking_datetime=booking_datetime,
        passenger_age=passenger_age,
        luggage_kg=Decimal(luggage_kg),
        seat_extra=seat.extra_cost,
    )

    with transaction.atomic():
        seat.is_booked = True
        seat.save()

        booking = Booking.objects.create(
            user=user,
            flight=flight,
            seat=seat,
            passenger_name=passenger_name,
            passenger_age=passenger_age,
            luggage_kg=Decimal(luggage_kg),
            price_paid=final_price,
            status=Booking.CONFIRMED,
            confirmation_code=str(uuid.uuid4()),
        )

    return booking, {'pricing_breakdown': breakdown}

