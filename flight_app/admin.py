from django.contrib import admin
from .models import Airline, Flight, Seat, Booking

@admin.register(Airline)
class AirlineAdmin(admin.ModelAdmin):
    list_display = ('name','code','service_tier')

@admin.register(Flight)
class FlightAdmin(admin.ModelAdmin):
    list_display = ('flight_number','airline','origin','destination','departure','base_price')

@admin.register(Seat)
class SeatAdmin(admin.ModelAdmin):
    list_display = ('flight','seat_number','seat_class','is_booked','extra_cost')

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('id','passenger_name','flight','seat','price_paid','status','confirmation_code','created_at')
    readonly_fields = ('confirmation_code','created_at')
