"""
Tests for user API.
"""

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from user.models import User
from user.serializers import UserDetailsSerializer

TOKEN_URL = reverse("authenticate")
CREATE_USER_URL = reverse("user:create-user")
PROFILE_URL = reverse("user:me")
FOLLOW_URL = lambda username: reverse("user:follow", kwargs={"username": username})
UNFOLLOW_URL = lambda username: reverse("user:unfollow", kwargs={"username": username})


def create_user(**fields):
    """Creates a new user with given fields and returns the new user."""

    return User.objects.create_user(**fields)


class UnauthorizedUserTests(TestCase):
    """Tests for unauthorized user"""

    def setUp(self):
        self.client = APIClient()

    def test_user_creation_successful(self):
        """Test new user creation is successful"""

        payload = {
            "email": "user1@example.com",
            "password": "user1pass",
            "name": "User1",
        }

        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(email=payload["email"])
        self.assertTrue(user.check_password(payload["password"]))
        self.assertIn("username", res.data)
        self.assertNotIn("password", res.data)

    def test_user_creation_with_email_missing(self):
        """Test new user creation with email field missing is not successful"""

        payload = {"password": "user1pass", "name": "User1"}
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_creation_with_password_missing(self):
        """Test new user creation with password field missing is not successful"""

        payload = {"email": "user1@example.com", "name": "User1"}
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_creation_with_name_missing(self):
        """Test new user creation with name field missing is not successful"""

        payload = {
            "email": "user1@example.com",
            "password": "user1pass",
        }
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_jwt_token_creation_successful(self):
        """Test jwt token creation is successful"""

        payload = {
            "email": "user1@example.com",
            "password": "user1pass",
            "name": "User1",
        }
        user = create_user(**payload)
        token_payload = {"username": user.username, "password": payload["password"]}
        res = self.client.post(TOKEN_URL, token_payload)
        self.assertIn("access", res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_jwt_token_creation_with_username_missing(self):
        """Test jwt token creation with username field missing is not successful"""

        payload = {
            "email": "user1@example.com",
            "password": "user1pass",
            "name": "User1",
        }
        user = create_user(**payload)
        token_payload = {"password": payload["password"]}
        res = self.client.post(TOKEN_URL, token_payload)
        self.assertNotIn("access", res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_jwt_token_creation_with_password_missing(self):
        """Test jwt token creation with password field missing is not successful"""

        payload = {
            "email": "user1@example.com",
            "password": "user1pass",
            "name": "User1",
        }
        user = create_user(**payload)
        token_payload = {"username": user.username}
        res = self.client.post(TOKEN_URL, token_payload)
        self.assertNotIn("access", res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_unauthorized(self):
        """Test retrieving user profile of unauthorized is not successful"""

        res = self.client.get(PROFILE_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthorizedUserTests(TestCase):
    """Tests for authorized user"""

    def setUp(self):
        self.user1 = create_user(
            email="user1@example.com", password="user1pass", name="User1"
        )
        self.user2 = create_user(
            email="user2@example.com", password="user2pass", name="User2"
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user1)

    def test_retrieve_user_authorized(self):
        """Test retrieving user profile of authorized is successful"""

        serializer = UserDetailsSerializer(self.user1)
        res = self.client.get(PROFILE_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_follow_user_with_given_username_successful(self):
        """Test following user with given username is successful"""

        res = self.client.post(FOLLOW_URL(self.user2.username))
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        temp_user1 = User.objects.get(username=self.user1.username)
        temp_user2 = User.objects.get(username=self.user2.username)
        user1_following_list = [
            user.following.username for user in temp_user1.following.all()
        ]
        user2_follower_list = [
            user.follower.username for user in temp_user2.follower.all()
        ]
        self.assertIn(self.user2.username, user1_following_list)

    def test_unfollow_user_with_given_username_successful(self):
        """Test unfollowing user with given username is successful"""

        res = self.client.post(FOLLOW_URL(self.user2.username))
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        res = self.client.delete(UNFOLLOW_URL(self.user2.username))
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        temp_user1 = User.objects.get(username=self.user1.username)
        temp_user2 = User.objects.get(username=self.user2.username)
        user1_following_list = [
            user.following.username for user in temp_user1.following.all()
        ]
        user2_follower_list = [
            user.follower.username for user in temp_user2.follower.all()
        ]
        self.assertNotIn("user2", user1_following_list)
