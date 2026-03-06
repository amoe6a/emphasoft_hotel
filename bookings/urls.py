from django.urls import path
from . import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenBlacklistView,
)

urlpatterns = [
    path("rooms/", views.room_list, name="room_list"),
    path("book/", views.book_room, name="book_room"),
    path("book/<int:room_id>/", views.book_room, name="book_room_with_given_room_id"),
    path("my-bookings/", views.my_bookings, name="my_bookings"),
    path("cancel_booking/<int:pk>/", views.cancel_booking, name="cancel_booking"),
    path("register/", views.register, name="register"),
    path("api/login/", TokenObtainPairView.as_view(), name="api_login"),
    path("api/logout/", TokenBlacklistView.as_view(), name="token_blacklist"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/register/", views.RegisterAPIView.as_view(), name="api_register"),
    path("api/rooms/", views.RoomListAPIView.as_view(), name="room_list_api"),
    path("api/book/", views.BookRoomAPIView.as_view(), name="book_room_api"),
    path("api/my-bookings/", views.MyBookingsAPIView.as_view(), name="my_bookings_api"),
    path(
        "api/cancel_booking_api/<int:pk>",
        views.CancelBookingAPIView.as_view(),
        name="cancel_booking_api",
    ),
]
