from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


# Create your models here.
class Room(models.Model):
    name = models.CharField(max_length=100)
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)
    capacity = models.PositiveBigIntegerField()
    is_empty = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Booking(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()

    @property
    def total_price(self) -> models.DecimalField:
        return self.room.price_per_night * (self.end_date - self.start_date).days

    def clean(self):
        super().clean()

        if self.room and self.start_date and self.end_date:
            if self.start_date > self.end_date:
                raise ValidationError("Invalid dates range")

            time_clashes = Booking.objects.filter(
                room=self.room,
                start_date__lte=self.end_date,
                end_date__gte=self.start_date,
            )

            # if admin wants to modify the existing booking
            if self.pk:
                time_clashes = time_clashes.exclude(pk=self.pk)

            if time_clashes.exists():
                raise ValidationError("Room won't be fully available for these dates")
