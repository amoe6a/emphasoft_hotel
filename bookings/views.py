from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Room, Booking
from .forms import BookingForm
from django.contrib.auth.forms import UserCreationForm

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .serializers import RoomSerializer, BookingSerializer

from .filters import RoomFilter


def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Account created.")
            return redirect("login")
    else:
        form = UserCreationForm()

    return render(request, "registration/register.html", {"form": form})


@api_view(["GET"])
def room_list_api(request):
    rooms_filtered = RoomFilter(request.GET, queryset=Room.objects.all())
    serilized_rooms = RoomSerializer(rooms_filtered.qs, many=True)
    return Response(serilized_rooms.data)


def room_list(request):
    rooms_filtered = RoomFilter(request.GET, queryset=Room.objects.all())
    return render(request, "bookings/room_list.html", {"rooms": rooms_filtered.qs})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def book_room_api(request):
    serialized_booking = BookingSerializer(data=request.data)
    if serialized_booking.is_valid():
        serialized_booking.save(user=request.user)
        return Response(serialized_booking.data, status=status.HTTP_201_CREATED)
    return Response(serialized_booking.errors, status=status.HTTP_400_BAD_REQUEST)


def book_room(request):
    if request.method == "POST":
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.save()
            messages.success(request, "Your room is booked!")
            return redirect("room_list")
    else:
        form = BookingForm()
    return render(request, "bookings/book_room.html", {"form": form})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def my_bookings_api(request):
    bookings = Booking.objects.filter(user=request.user)
    serialized_bookings = BookingSerializer(bookings, many=True)
    return Response(serialized_bookings.data)


@login_required
def my_bookings(request):
    user_bookings = Booking.objects.filter(user=request.user)
    return render(request, "bookings/my_bookings.html", {"bookings": user_bookings})


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def cancel_booking_api(request, pk):
    booking = get_object_or_404(Booking, pk=pk, user=request.user)
    booking.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


def cancel_booking(request, pk):
    booking = get_object_or_404(Booking, pk=pk, user=request.user)
    booking.delete()
    return redirect("my_bookings")
