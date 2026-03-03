from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Room, Booking
from .forms import BookingForm
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse, HttpResponseRedirect

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .serializers import RoomSerializer, BookingSerializer

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
            name="end_date", type=date, description="Filter by availability end_date"
        ),
    ],
    responses={200: RoomSerializer(many=True)},
    description="Search for available rooms within a price range and specific dates.",
)
@api_view(["GET"])
def room_list_api(request) -> Response:
    rooms_filtered = RoomFilter(request.GET, queryset=Room.objects.all())
    serilized_rooms = RoomSerializer(rooms_filtered.qs, many=True)
    return Response(serilized_rooms.data)


def room_list(request) -> HttpResponse:
    rooms_filtered = RoomFilter(request.GET, queryset=Room.objects.all())
    return render(
        request,
        "bookings/room_list.html",
        {"filter": rooms_filtered, "rooms": rooms_filtered.qs},
    )


@extend_schema(
    request=BookingSerializer,
    responses={201: BookingSerializer},
    description="Allows authenticated user to book a room. Requires room id and date range.",
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def book_room_api(request) -> Response:
    serialized_booking = BookingSerializer(data=request.data)
    if serialized_booking.is_valid():
        serialized_booking.save(user=request.user)
        return Response(serialized_booking.data, status=status.HTTP_201_CREATED)
    return Response(serialized_booking.errors, status=status.HTTP_400_BAD_REQUEST)


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


@extend_schema(
    responses={200: BookingSerializer(many=True)},
    description="Retrieves a list of all bookings made by the currently authenticated user.",
    tags=["User Bookings"],
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def my_bookings_api(request) -> Response:
    bookings = Booking.objects.filter(user=request.user)
    serialized_bookings = BookingSerializer(bookings, many=True)
    return Response(serialized_bookings.data)


@login_required
def my_bookings(request) -> HttpResponse:
    user_bookings = Booking.objects.filter(user=request.user)
    return render(request, "bookings/my_bookings.html", {"bookings": user_bookings})


@extend_schema(
    parameters=[
        OpenApiParameter(
            name="pk",
            description="The unique ID of the booking to cancel",
            type=int,
            location=OpenApiParameter.PATH,
        )
    ],
    responses={204: None},
    description="Deletes a booking record. Users can only delete their own bookings.",
)
@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def cancel_booking_api(request, pk) -> Response:
    booking = get_object_or_404(Booking, pk=pk, user=request.user)
    booking.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


def cancel_booking(request, pk) -> HttpResponseRedirect:
    booking = get_object_or_404(Booking, pk=pk, user=request.user)
    booking.delete()
    return redirect("my_bookings")
