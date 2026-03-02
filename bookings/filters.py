import django_filters
from .models import Room
from django.core.exceptions import ValidationError

class RoomFilter(django_filters.FilterSet):
    start_date = django_filters.DateFilter(method='filter_available_dates')
    end_date = django_filters.DateFilter(method='filter_available_dates')

    class Meta:
        model = Room
        fields = {
            'capacity': ['exact'],
            'price_per_night': ['lte', 'gte'],
        }

    def filter_available_dates(self, queryset, name, value):
        if name == 'end_date':
            start = self.data.get('start_date')
            end = value
            if start and end:
                return queryset.exclude(
                    booking__start_date__lt=end,
                    booking__end_date__gt=start
                )
            else:
                raise ValidationError("Please provide both check-in and check-out dates")
        elif name == 'start_date':
            start = value
            end = self.data.get('end_date')
            if not (start and end):
                raise ValidationError("Please provide both check-in and check-out dates")
        return queryset
