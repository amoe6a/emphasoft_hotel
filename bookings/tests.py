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

    def test_filter_by_capacity_gte(self):
        # Testing 'capacity': ['gte']
        response = self.client.get(reverse(self.url), {"capacity": 2})
        self.assertEqual(len(response.context["rooms"]), 3)

    def test_filter_by_price_range(self):
        # Testing 'price_per_night': ['lte', 'gte']
        # Looking for rooms between 1200 and 1800
        data = {"min_price": 1200, "max_price": 1800}
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

    def test_book_room_success(self):
        self.client.login(username="testuser", password="password")
        data = {
            "room": self.room_small.id,
            "start_date": "2026-05-10",
            "end_date": "2026-05-15",
        }
        response = self.client.post(reverse("book_room"), data)
        # Expect a redirect (status code 302) back to the room list
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("room_list"))

        self.assertEqual(Booking.objects.count(), 2)

    def test_prevent_double_booking(self):
        # Create a booking
        Booking.objects.create(
            user=self.user,
            room=self.room_small,
            start_date="2026-05-01",
            end_date="2026-05-05",
        )
        self.client.login(username="testuser", password="password")

        overlap_data = {
            "room": self.room_small.id,
            "start_date": "2026-05-04",
            "end_date": "2026-05-07",
        }
        # create an overlapping booking
        response = self.client.post(reverse("book_room"), overlap_data)

        # django will give 200 and stay on the same page
        self.assertEqual(response.status_code, 200)
        # Expect the exact error message from clean()
        errors = response.context["form"].non_field_errors()
        print(errors)
        self.assertIsNotNone(errors)
        # Ensure no new booking was created
        print([[b.room, b.start_date, b.end_date] for b in Booking.objects.all()])
        self.assertEqual(Booking.objects.count(), 2)

    def test_booking_requires_login(self):
        # Ensure we are not logged in
        self.client.logout()
        # Try access the booking page
        response = self.client.get(reverse("book_room"))
        # Verify the redirect
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response.url)

    def test_cannot_cancel_others_booking(self):
        other_user = User.objects.create_user(
            username="intruder", password="password123"
        )

        # 2. Create a booking belonging to second user
        others_booking = Booking.objects.create(
            user=other_user,
            room=self.room_mid,
            start_date="2026-06-01",
            end_date="2026-06-05",
        )

        # Log in as the FIRST user (testuser)
        self.client.login(username="testuser", password="password")

        url = reverse("cancel_booking", kwargs={"pk": others_booking.pk})
        response = self.client.post(url)

        # Verify the security block
        self.assertEqual(response.status_code, 404)

        # Booking should still exist
        self.assertTrue(Booking.objects.filter(pk=others_booking.pk).exists())
