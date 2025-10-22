from rest_framework import serializers
from .models import Flight, Seat, Booking, Airline

class AirlineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airline
        fields = '__all__'


class FlightSerializer(serializers.ModelSerializer):
    airline = AirlineSerializer(read_only=True)
    class Meta:
        model = Flight
        fields = '__all__'


class SeatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seat
        fields = '__all__'


class BookingSerializer(serializers.ModelSerializer):
    flight = FlightSerializer(read_only=True)
    seat = SeatSerializer(read_only=True)
    class Meta:
        model = Booking
        fields = '__all__'
        read_only_fields = ('price_paid','status','confirmation_code','created_at')

