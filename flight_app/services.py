from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime, timezone
import uuid
from django.db import transaction
from .models import Booking, Seat

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


def generate_pnr():
    return uuid.uuid4().hex[:12].upper()


def calculate_price(
    base_price: Decimal,
    seat_class: str,
    airline_service: str,
    departure_datetime,
    booking_datetime=None,
    passenger_age: int = 30,
    luggage_kg: Decimal = Decimal('0'),
    seat_extra: Decimal = Decimal('0')
):
    if booking_datetime is None:
        booking_datetime = datetime.now(timezone.utc)

    price = Decimal(base_price)
    price *= SEAT_CLASS_MULTIPLIER.get(seat_class, 1)
    price *= AIRLINE_SERVICE_MULTIPLIER.get(airline_service, 1)
    price += Decimal(seat_extra)

    # luggage surcharge
    if luggage_kg > INCLUDED_LUGGAGE_KG:
        price += (luggage_kg - INCLUDED_LUGGAGE_KG) * EXTRA_LUGGAGE_RATE_PER_KG

    # time-based multiplier
    delta_days = (departure_datetime - booking_datetime).total_seconds() / 86400
    if delta_days <= 3:
        price *= Decimal('1.50')
    elif delta_days <= 7:
        price *= Decimal('1.25')
    elif delta_days <= 30:
        price *= Decimal('1.05')

    # age-based discount
    if passenger_age <= AGE_DISCOUNTS['child_max_age']:
        price *= AGE_DISCOUNTS['child_discount']
    elif passenger_age >= AGE_DISCOUNTS['senior_min_age']:
        price *= AGE_DISCOUNTS['senior_discount']

    return _round(price)


def simulate_payment(success=True):
    return success


def book_seat(user, flight, seat, passenger_name, passenger_age, luggage_kg):
    if seat.is_booked:
        return None, "Seat already booked"

    with transaction.atomic():
        # Lock seat for concurrency safety
        seat = Seat.objects.select_for_update().get(pk=seat.pk)
        if seat.is_booked:
            return None, "Seat already booked"

        price = calculate_price(
            base_price=flight.base_price,
            seat_class=seat.seat_class,
            airline_service=flight.airline.service_tier,
            departure_datetime=flight.departure,
            passenger_age=passenger_age,
            luggage_kg=luggage_kg,
            seat_extra=seat.extra_cost
        )

        if not simulate_payment(True):
            return None, "Payment failed"

        seat.is_booked = True
        seat.save()

        booking = Booking.objects.create(
            user=user,
            flight=flight,
            seat=seat,
            passenger_name=passenger_name,
            passenger_age=passenger_age,
            luggage_kg=luggage_kg,
            price_paid=price,
            status=Booking.CONFIRMED,
            pnr=generate_pnr()
        )

    return booking, None


def cancel_booking(booking):
    with transaction.atomic():
        booking.status = Booking.CANCELLED
        booking.seat.is_booked = False
        booking.seat.save()
        booking.save()


def get_booking_history(user):
    return Booking.objects.filter(user=user).order_by('-created_at')
