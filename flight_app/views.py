from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Flight, Seat, Booking, Airline
from .serializers import FlightSerializer, SeatSerializer, BookingSerializer
from .services import calculate_price, book_seat_and_create_booking
from decimal import Decimal
from datetime import datetime, timezone

class FlightSearchView(APIView):
    def get(self, request):
        qs = Flight.objects.all()
        origin = request.query_params.get('origin')
        dest = request.query_params.get('destination')
        date = request.query_params.get('date')
        airline_code = request.query_params.get('airline_code')
        if origin: qs = qs.filter(origin__iexact=origin)
        if dest: qs = qs.filter(destination__iexact=dest)
        if date: qs = qs.filter(departure__date=date)
        if airline_code: qs = qs.filter(airline__code__iexact=airline_code)
        serializer = FlightSerializer(qs, many=True)
        return Response(serializer.data)


class SeatListView(APIView):
    def get(self, request, flight_id):
        flight = get_object_or_404(Flight, pk=flight_id)
        seats = flight.seats.all()
        serializer = SeatSerializer(seats, many=True)
        return Response(serializer.data)


class PriceQuoteView(APIView):
    def post(self, request):
        data = request.data
        flight = get_object_or_404(Flight, pk=data.get('flight_id'))
        seat = get_object_or_404(Seat, pk=data.get('seat_id'), flight=flight)
        booking_dt = datetime.now(timezone.utc)
        final, breakdown = calculate_price(
            base_price=flight.base_price,
            seat_class=seat.seat_class,
            airline_service=flight.airline.service_tier,
            departure_datetime=flight.departure,
            booking_datetime=booking_dt,
            passenger_age=int(data.get('passenger_age', 30)),
            luggage_kg=Decimal(str(data.get('luggage_kg', 0))),
            seat_extra=seat.extra_cost,
        )
        return Response({'final_price': str(final), 'breakdown': breakdown})


class BookSeatView(APIView):
    def post(self, request):
        data = request.data
        flight = get_object_or_404(Flight, pk=data.get('flight_id'))
        seat = get_object_or_404(Seat, pk=data.get('seat_id'), flight=flight)
        user = request.user if request.user.is_authenticated else None
        booking, info = book_seat_and_create_booking(
            user=user,
            flight=flight,
            seat=seat,
            passenger_name=data.get('passenger_name', 'Passenger'),
            passenger_age=int(data.get('passenger_age', 30)),
            luggage_kg=Decimal(str(data.get('luggage_kg', 0))),
        )
        if not booking:
            return Response({'error': info}, status=status.HTTP_400_BAD_REQUEST)
        serializer = BookingSerializer(booking)
        response_data = serializer.data
        response_data['pricing_breakdown'] = info.get('pricing_breakdown', {})
        return Response(response_data, status=status.HTTP_201_CREATED)


class BookingDetailView(APIView):
    def get(self, request, booking_id):
        booking = get_object_or_404(Booking, pk=booking_id)
        serializer = BookingSerializer(booking)
        return Response(serializer.data)

