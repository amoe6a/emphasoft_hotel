from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Room, Booking
from .filters import RoomFilter


class RoomFilterTest(TestCase):
    url = "room_list"

    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password")
        self.room_small = Room.objects.create(
            name="101", price_per_night=1000, capacity=2
        )
        self.room_large = Room.objects.create(
            name="102", price_per_night=2000, capacity=4
        )
        self.room_mid = Room.objects.create(
            name="103", price_per_night=1500, capacity=2
        )

        # Room 101 is booked from Feb 12 to Feb 18
        Booking.objects.create(
            room=self.room_small,
            start_date="2026-02-12",
            end_date="2026-02-18",
            user=self.user,
        )

    def test_filter_by_capacity_exact(self):
        # Testing 'capacity': ['exact']
        response = self.client.get(reverse(self.url), {"capacity": 2})
        self.assertEqual(len(response.context["rooms"]), 2)

    def test_filter_by_price_range(self):
        # Testing 'price_per_night': ['lte', 'gte']
        # Looking for rooms between 1200 and 1800
        data = {"price_per_night__gte": 1200, "price_per_night__lte": 1800}
        response = self.client.get(reverse(self.url), data)
        self.assertEqual(len(response.context["rooms"]), 1)
        self.assertEqual(response.context["rooms"][0].name, "103")

    def test_filter_available_dates_exclusion(self):
        # Request for Feb 10 to Feb 15.
        # Room 101 (booked Feb 12-18) should be excluded.
        data = {"start_date": "2026-02-10", "end_date": "2026-02-15"}
        response = self.client.get(reverse(self.url), data)

        # Room 101 is excluded, so 102 and 103 should remain
        self.assertEqual(len(response.context["rooms"]), 2)
        # Verify Room 101 was not included
        room_names = [r.name for r in response.context["rooms"]]
        self.assertNotIn("101", room_names)

    def test_filter_requires_both_dates(self):
        # Only provide the start_date and expect ValidationError
        data = {"start_date": "2026-02-10"}
        with self.assertRaises(ValidationError):
            rooms_filter = RoomFilter(data, queryset=Room.objects.all())
            rooms_filter.qs
