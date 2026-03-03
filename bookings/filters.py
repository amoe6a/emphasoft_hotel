import django_filters
from django import forms
from .models import Room
from django.core.exceptions import ValidationError
from django.db.models import QuerySet


class RoomFilter(django_filters.FilterSet):
    start_date = django_filters.DateFilter(
        widget=forms.DateInput(attrs={"type": "date"}), method="filter_available_dates"
    )
    end_date = django_filters.DateFilter(
        widget=forms.DateInput(attrs={"type": "date"}), method="filter_available_dates"
    )

    min_price = django_filters.NumberFilter(
        field_name="price_per_night",
        lookup_expr="gte",
        label="Min Price",
        widget=forms.NumberInput(attrs={"placeholder": "Min"}),
    )
    max_price = django_filters.NumberFilter(
        field_name="price_per_night",
        lookup_expr="lte",
        label="Max Price",
        widget=forms.NumberInput(attrs={"placeholder": "Max"}),
    )

    ordering_filter = django_filters.OrderingFilter(
        fields=(
            ("price_per_night", "price"),
            ("capacity", "capacity"),
        ),
        field_labels={
            "price_per_night": "Price",
            "capacity": "Capacity",
        },
    )

    class Meta:
        model = Room
        fields = {
            "capacity": ["gte"],
        }

    def filter_available_dates(self, queryset, name, value) -> QuerySet[Room]:
        if name == "end_date":
            start = self.data.get("start_date")
            end = value
            if start and end:
                return queryset.exclude(
                    booking__start_date__lt=end, booking__end_date__gt=start
                )
            else:
                raise ValidationError(
                    "Please provide both check-in and check-out dates"
                )
        elif name == "start_date":
            start = value
            end = self.data.get("end_date")
            if not (start and end):
                raise ValidationError(
                    "Please provide both check-in and check-out dates"
                )
        return queryset
