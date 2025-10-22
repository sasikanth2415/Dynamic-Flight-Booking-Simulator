from django.urls import path
from .views import BookFlightView, CancelBookingView, BookingHistoryView, FlightSearchView, SeatListView

urlpatterns = [
    path('flights/search/', FlightSearchView.as_view(), name='flight-search'),
    path('flights/<int:flight_id>/seats/', SeatListView.as_view(), name='seat-list'),
    path('book/', BookFlightView.as_view(), name='book-flight'),
    path('cancel/<int:booking_id>/', CancelBookingView.as_view(), name='cancel-booking'),
    path('history/', BookingHistoryView.as_view(), name='booking-history'),
]
