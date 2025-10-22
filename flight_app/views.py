from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Flight, Seat, Booking
from .serializers import BookingSerializer, FlightSerializer, SeatSerializer
from .services import book_seat, cancel_booking, get_booking_history
from decimal import Decimal

class BookFlightView(APIView):
    def post(self, request):
        data = request.data
        flight = get_object_or_404(Flight, pk=data.get('flight_id'))
        seat = get_object_or_404(Seat, pk=data.get('seat_id'), flight=flight)
        user = request.user if request.user.is_authenticated else None

        booking, error = book_seat(
            user=user,
            flight=flight,
            seat=seat,
            passenger_name=data.get('passenger_name'),
            passenger_age=int(data.get('passenger_age', 30)),
            luggage_kg=Decimal(str(data.get('luggage_kg', 0))),
        )

        if error:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)

        serializer = BookingSerializer(booking)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CancelBookingView(APIView):
    def post(self, request, booking_id):
        booking = get_object_or_404(Booking, pk=booking_id)
        cancel_booking(booking)
        return Response({'status': 'cancelled'})


class BookingHistoryView(APIView):
    def get(self, request):
        user = request.user
        bookings = get_booking_history(user)
        serializer = BookingSerializer(bookings, many=True)
        return Response(serializer.data)


class FlightSearchView(APIView):
    def get(self, request):
        origin = request.query_params.get('origin')
        destination = request.query_params.get('destination')
        flights = Flight.objects.all()
        if origin:
            flights = flights.filter(origin__iexact=origin)
        if destination:
            flights = flights.filter(destination__iexact=destination)
        serializer = FlightSerializer(flights, many=True)
        return Response(serializer.data)


class SeatListView(APIView):
    def get(self, request, flight_id):
        flight = get_object_or_404(Flight, pk=flight_id)
        seats = flight.seats.all()
        serializer = SeatSerializer(seats, many=True)
        return Response(serializer.data)
