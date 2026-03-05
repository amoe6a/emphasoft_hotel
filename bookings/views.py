from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Room, Booking
from .forms import BookingForm
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse, HttpResponseRedirect
from django.db.models import QuerySet
from django.contrib.auth.models import User

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import generics
from rest_framework.request import Request
from rest_framework.permissions import AllowAny
from .serializers import RoomSerializer, BookingSerializer, UserRegistrationSerializer

from drf_spectacular.utils import extend_schema, OpenApiParameter

from .filters import RoomFilter
from datetime import date


def register(request) -> HttpResponse:
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Account created.")
            return redirect("login")
    else:
        form = UserCreationForm()

    return render(request, "registration/register.html", {"form": form})


def room_list(request) -> HttpResponse:
    rooms_filtered = RoomFilter(request.GET, queryset=Room.objects.all())
    return render(
        request,
        "bookings/room_list.html",
        {"filter": rooms_filtered, "rooms": rooms_filtered.qs},
    )


@login_required
def book_room(request, room_id=None) -> HttpResponse:
    if request.method == "POST":
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.save()
            messages.success(request, "Your room is booked!")
            return redirect("room_list")
    else:
        if room_id:
            room = get_object_or_404(Room, id=room_id)
            form = BookingForm({"room": room})
        else:
            form = BookingForm()
    return render(request, "bookings/book_room.html", {"form": form})


@login_required
def my_bookings(request) -> HttpResponse:
    user_bookings = Booking.objects.filter(user=request.user)
    return render(request, "bookings/my_bookings.html", {"bookings": user_bookings})


def cancel_booking(request, pk) -> HttpResponseRedirect:
    booking = get_object_or_404(Booking, pk=pk, user=request.user)
    booking.delete()
    return redirect("my_bookings")


class RegisterAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

    @extend_schema(description="Creates a new user account via JSON payload.")
    def post(self, request, *args, **kwargs) -> Response:
        return super().post(request, *args, **kwargs)


class RoomListAPIView(generics.ListAPIView):
    serializer_class = RoomSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="min_price",
                type=float,
                description="Filter by minimum price per night",
            ),
            OpenApiParameter(
                name="max_price",
                type=float,
                description="Filter by maximum price per night",
            ),
            OpenApiParameter(
                name="start_date", type=date, description="Filter by start_date"
            ),
            OpenApiParameter(
                name="end_date", type=date, description="Filter by end_date"
            ),
        ],
        description="Search for available rooms within a price range and specific dates.",
    )
    def get(self, request: Request, *args, **kwargs) -> Response:
        return super().get(request, *args, **kwargs)

    def get_queryset(self) -> QuerySet[Room]:
        return RoomFilter(self.request.GET, queryset=Room.objects.all()).qs


class BookRoomAPIView(generics.CreateAPIView):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        description="Allows authenticated user to book a room. Requires room id and date range."
    )
    def post(self, request: Request, *args, **kwargs) -> Response:
        return super().post(request, *args, **kwargs)

    def perform_create(self, serializer: BookingSerializer) -> None:
        serializer.save(user=self.request.user)


class MyBookingsAPIView(generics.ListAPIView):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        description="Retrieves a list of all bookings made by the currently authenticated user.",
        tags=["User Bookings"],
    )
    def get(self, request: Request, *args, **kwargs) -> Response:
        return super().get(request, *args, **kwargs)

    def get_queryset(self) -> QuerySet[Booking]:
        return Booking.objects.filter(user=self.request.user)


class CancelBookingAPIView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="pk",
                description="The unique ID of the booking to cancel",
                type=int,
                location=OpenApiParameter.PATH,
            )
        ],
        description="Deletes a booking record. Users can only delete their own bookings.",
    )
    def delete(self, request: Request, *args, **kwargs) -> Response:
        return super().delete(request, *args, **kwargs)

    def get_queryset(self) -> QuerySet[Booking]:
        return Booking.objects.filter(user=self.request.user)
