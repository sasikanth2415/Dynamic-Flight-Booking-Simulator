from django.urls import path
from .views import FlightSearchView, SeatListView, PriceQuoteView, BookSeatView, BookingDetailView

urlpatterns = [
    path('flights/search/', FlightSearchView.as_view(), name='flight-search'),
    path('flights/<int:flight_id>/seats/', SeatListView.as_view(), name='seat-list'),
    path('quote/price/', PriceQuoteView.as_view(), name='price-quote'),
    path('book/', BookSeatView.as_view(), name='book-seat'),
    path('booking/<int:booking_id>/', BookingDetailView.as_view(), name='booking-detail'),
]

