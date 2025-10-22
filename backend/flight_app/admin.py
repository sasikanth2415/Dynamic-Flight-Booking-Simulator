from django.contrib import admin
from .models import Airline, Flight, Seat, Booking

admin.site.register(Airline)
admin.site.register(Flight)
admin.site.register(Seat)
admin.site.register(Booking)
