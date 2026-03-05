from rest_framework import serializers
from .models import Room, Booking
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ("username", "password")

    def create(self, validated_data: dict) -> User:
        return User.objects.create_user(**validated_data)


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = "__all__"


class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = "__all__"
        extra_kwargs = {"user": {"read_only": True}}

    def validate(self, data):
        temp_instance = Booking(**data)
        try:
            temp_instance.clean()
        except ValidationError as e:
            raise serializers.ValidationError({"non_field_errors": e.messages})
        return data
