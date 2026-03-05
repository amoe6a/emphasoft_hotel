from django.test import TestCase, TransactionTestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Room, Booking
from .filters import RoomFilter
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

import concurrent.futures
from django.db import connection


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
        self.assertIsNotNone(errors)
        # Ensure no new booking was created
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


class UserRegistrationAPITest(APITestCase):
    def setUp(self) -> None:
        self.url = reverse("api_register")
        self.user_data = {
            "username": "new_guest",
            "password": "password123",
        }

    def test_registration_success(self) -> None:
        response = self.client.post(self.url, data=self.user_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().username, "new_guest")

        # Ensure password is not returned
        self.assertNotIn("password", response.data)

    def test_registration_missing_fields(self) -> None:
        incomplete_data = {"password": "password123"}
        response = self.client.post(self.url, data=incomplete_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("username", response.data)

    def test_registration_duplicate_username(self) -> None:
        # Create an existing user first
        User.objects.create_user(username="new_guest", password="password")

        response = self.client.post(self.url, data=self.user_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("username", response.data)


class JWTLoginAPITest(APITestCase):
    def setUp(self) -> None:
        self.username = "test_user"
        self.password = "secure_pass_123"
        self.user = User.objects.create_user(
            username=self.username, password=self.password
        )
        self.url = reverse("token_obtain_pair")

    def test_login_success_returns_jwt(self) -> None:
        data = {"username": self.username, "password": self.password}
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check for 'access' and 'refresh' keys
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_login_invalid_password(self) -> None:
        data = {"username": self.username, "password": "wrong_password"}
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotIn("access", response.data)

    def test_token_refresh(self) -> None:
        login_data = {"username": self.username, "password": self.password}
        login_response = self.client.post(self.url, login_data, format="json")
        refresh_token = login_response.data["refresh"]

        refresh_url = reverse("token_refresh")
        refresh_response = self.client.post(
            refresh_url, {"refresh": refresh_token}, format="json"
        )

        self.assertEqual(refresh_response.status_code, status.HTTP_200_OK)
        self.assertIn("access", refresh_response.data)


class BookingRaceConditionTest(TransactionTestCase):
    def setUp(self):
        # Two distinct users
        self.user1 = User.objects.create_user(username="raceuser1", password="password")
        self.user2 = User.objects.create_user(username="raceuser2", password="password")

        self.room = Room.objects.create(
            name="testroom", price_per_night=1000, capacity=2
        )
        self.url = reverse("book_room_api")
        self.payload = {
            "room": self.room.id,
            "start_date": "2026-08-10",
            "end_date": "2026-08-15",
        }

    def test_concurrent_double_booking(self):
        def make_request(user: User) -> int:
            thread_client = APIClient()

            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            thread_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

            response = thread_client.post(self.url, data=self.payload, format="json")
            connection.close()
            return response.status_code

        # Fire two identical requests at the exact same time with different users
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            users = [self.user1, self.user2]
            futures = [executor.submit(make_request, user) for user in users]
            results = [
                future.result() for future in concurrent.futures.as_completed(futures)
            ]
        self.assertIn(
            status.HTTP_201_CREATED, results, "One request should have succeeded."
        )
        # I realised this will hardly ever give 409 during the test, because of the GIL
        has_either_40x = (
            status.HTTP_409_CONFLICT in results
            or status.HTTP_400_BAD_REQUEST in results
        )
        self.assertTrue(has_either_40x, "The second should have returned a 409 or 400")

        booking_count = Booking.objects.filter(room=self.room).count()
        self.assertEqual(
            booking_count,
            1,
            "The database should contain exactly 1 booking for this room.",
        )
