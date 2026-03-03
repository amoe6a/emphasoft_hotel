from django import forms
from .models import Booking
from django.core.exceptions import ValidationError


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ["room", "start_date", "end_date"]
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "end_date": forms.DateInput(attrs={"type": "date"}),
        }

    def clean(self):
        cleaned_data = super().clean()
        room = cleaned_data.get("room")
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")

        if room and start_date and end_date:
            time_clashes = Booking.objects.filter(
                room=room, start_date__lte=end_date, end_date__gte=start_date
            )
            if time_clashes.exists():
                raise ValidationError("Room won't be fully available for these dates")

        return cleaned_data
