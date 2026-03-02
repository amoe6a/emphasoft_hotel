from rest_framework import serializers
from .models import Room, Booking

class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        # '__all__' tells Django to automatically translate every column in the database
        fields = '__all__' 

class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = '__all__'