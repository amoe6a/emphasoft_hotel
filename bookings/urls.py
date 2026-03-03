from django.urls import path
from . import views

urlpatterns = [
    path("rooms/", views.room_list, name="room_list"),
    path("book/", views.book_room, name="book_room"),
    path("my-bookings/", views.my_bookings, name="my_bookings"),
    path("cancel_booking/<int:pk>/", views.cancel_booking, name="cancel_booking"),
    path("register/", views.register, name="register"),
    path("api/rooms/", views.room_list_api, name="room_list_api"),
    path("api/book/", views.book_room_api, name="book_room_api"),
    path("api/my-bookings/", views.my_bookings_api, name="my_bookings_api"),
    path(
        "api/cancel_booking_api/<int:pk>",
        views.cancel_booking_api,
        name="cancel_booking_api",
    ),
]
