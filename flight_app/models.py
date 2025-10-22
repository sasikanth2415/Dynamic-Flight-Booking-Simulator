from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

SEAT_CLASS_CHOICES = [
    ('economy', 'Economy'),
    ('premium', 'Premium Economy'),
    ('business', 'Business'),
    ('first', 'First Class'),
]

AIRLINE_SERVICE_CHOICES = [
    ('basic', 'Basic'),
    ('comfort', 'Comfort'),
    ('premium', 'Premium'),
]

class Airline(models.Model):
    name = models.CharField(max_length=120)
    code = models.CharField(max_length=10, unique=True)
    service_tier = models.CharField(max_length=20, choices=AIRLINE_SERVICE_CHOICES, default='basic')

    def __str__(self):
        return f"{self.name} ({self.code})"


class Flight(models.Model):
    airline = models.ForeignKey(Airline, on_delete=models.CASCADE, related_name='flights')
    flight_number = models.CharField(max_length=20)
    origin = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)
    departure = models.DateTimeField()
    arrival = models.DateTimeField()
    base_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)

    class Meta:
        ordering = ['departure']

    def __str__(self):
        return f"{self.flight_number}: {self.origin} → {self.destination} @ {self.departure}"


class Seat(models.Model):
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE, related_name='seats')
    seat_number = models.CharField(max_length=8)
    seat_class = models.CharField(max_length=20, choices=SEAT_CLASS_CHOICES, default='economy')
    is_booked = models.BooleanField(default=False)
    extra_cost = models.DecimalField(max_digits=8, decimal_places=2, default=0.0)

    class Meta:
        unique_together = ('flight', 'seat_number')

    def __str__(self):
        return f"{self.flight.flight_number}-{self.seat_number} ({self.seat_class})"


class Booking(models.Model):
    PENDING = 'pending'
    CONFIRMED = 'confirmed'
    CANCELLED = 'cancelled'
    STATUS_CHOICES = [(PENDING, 'Pending'), (CONFIRMED, 'Confirmed'), (CANCELLED, 'Cancelled')]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE, related_name='bookings')
    seat = models.ForeignKey(Seat, on_delete=models.SET_NULL, null=True, blank=True)
    passenger_name = models.CharField(max_length=120)
    passenger_age = models.PositiveIntegerField()
    luggage_kg = models.DecimalField(max_digits=6, decimal_places=2, default=0.0)
    price_paid = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    confirmation_code = models.CharField(max_length=36, blank=True, null=True)

    def __str__(self):
        return f"Booking {self.id} - {self.passenger_name} ({self.status})"

