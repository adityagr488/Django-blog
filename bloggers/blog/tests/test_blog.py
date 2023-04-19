"""
Tests for the blog API
"""


from django.test import TestCase
from django.urls import reverse
from django.db.models import Count
from rest_framework.test import APIClient
from rest_framework import status
from user.models import User
from blog.models import Blog
from blog.serializers import BlogWithCommentsSerializer


CREATE_BLOG_URL = reverse("blog:create-blog")
BLOG_URL = lambda blog_id: reverse("blog:blog", kwargs={"id": blog_id})
MY_BLOGS_URL = reverse("blog:my-blogs")
ALL_BLOGS_URL = reverse("blog:all-blogs")
COMMENT_URL = lambda blog_id: reverse("blog:comment", kwargs={"id": blog_id})
LIKE_URL = lambda blog_id: reverse("blog:like", kwargs={"id": blog_id})
UNLIKE_URL = lambda blog_id: reverse("blog:unlike", kwargs={"id": blog_id})


def create_user(**fields):
    """Creates a new user with given fields and returns the new user."""

    return User.objects.create_user(**fields)


class UnAuthorizedUserBlogTests(TestCase):
    """Tests for unauthorized users."""

    def setUp(self):
        self.client = APIClient()

    def test_blog_creation_not_successful(self):
        """Test blog creation with an unauthorized user is not successful."""

        payload = {"title": "Test Post 1", "desc": "This is a test post"}
        res = self.client.post(CREATE_BLOG_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_comment_on_blog_with_given_id_not_successful(self):
        """Test comment on a blog with given id by an unauthorized user is not successful."""

        comment_payload = {"text": "This is a sample comment"}
        res = self.client.post(COMMENT_URL(1), comment_payload)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_like_blog_with_given_id_not_successful(self):
        """Test like on a blog with given id by an unauthorized user is not successful."""

        res = self.client.post(LIKE_URL(1))
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthorizedUserBlogTests(TestCase):
    """Tests for authorized users."""

    def setUp(self):
        self.user1 = create_user(
            email="user1@example.com", password="user1pass", name="User1"
        )
        self.user2 = create_user(
            email="user2@example.com", password="user2pass", name="User2"
        )
        self.client = APIClient()

    def test_blog_creation_successful(self):
        """Test blog creation with an authorized user is successful."""

        self.client.force_authenticate(user=self.user1)
        payload = {"title": "Test Post 1", "desc": "This is a test post"}
        res = self.client.post(CREATE_BLOG_URL, payload)
        new_blog = Blog.objects.get(id=res.data["id"])
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        for k, v in payload.items():
            self.assertEqual(getattr(new_blog, k), v)
        self.assertEqual(new_blog.author, self.user1)

    def test_blog_creation_with_title_field_missing(self):
        """Test blog creation with title field missing is not successful."""

        self.client.force_authenticate(user=self.user1)
        payload = {"desc": "This is a test post"}
        res = self.client.post(CREATE_BLOG_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn("id", res.data)

    def test_blog_creation_with_desc_field_missing(self):
        """Test blog creation with desc field missing is not successful."""

        self.client.force_authenticate(user=self.user1)
        payload = {"title": "Test Post 1"}
        res = self.client.post(CREATE_BLOG_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn("id", res.data)

    def test_retrieve_blog_with_given_id_successful(self):
        """Test retrieving blog with given id is successful."""

        self.client.force_authenticate(user=self.user1)
        payload = {"title": "Test Post 1", "desc": "This is a test post"}
        new_blog = self.client.post(CREATE_BLOG_URL, payload)
        res = self.client.get(BLOG_URL(new_blog.data["id"]))
        blog = Blog.objects.get(id=res.data["id"])
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        for k, v in payload.items():
            self.assertEqual(getattr(blog, k), v)

    def test_delete_blog_with_given_id_successful(self):
        """Test deleting blog with given id is successful."""

        self.client.force_authenticate(user=self.user1)
        payload = {"title": "Test Post 1", "desc": "This is a test post"}
        new_blog = self.client.post(CREATE_BLOG_URL, payload)
        res = self.client.delete(BLOG_URL(new_blog.data["id"]))
        blog_count = Blog.objects.filter(id=new_blog.data["id"]).count()
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(blog_count, 0)

    def test_comment_on_blog_with_given_id_successful(self):
        """Test comment on a blog with given id is successful."""

        self.client.force_authenticate(user=self.user1)
        blog_payload = {"title": "Test Post 1", "desc": "This is a test post"}
        new_blog = self.client.post(CREATE_BLOG_URL, blog_payload)
        comment_payload = {"text": "This is a sample comment"}
        res = self.client.post(COMMENT_URL(new_blog.data["id"]), comment_payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data["text"], comment_payload["text"])

    def test_comment_on_blog_with_text_field_missing(self):
        """Test comment on a blog with text field missing is not successful."""

        self.client.force_authenticate(user=self.user1)
        blog_payload = {"title": "Test Post 1", "desc": "This is a test post"}
        new_blog = self.client.post(CREATE_BLOG_URL, blog_payload)
        comment_payload = {}
        res = self.client.post(COMMENT_URL(new_blog.data["id"]), comment_payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_like_blog_with_given_id_successful(self):
        """Test like on a blog with given id is successful."""

        self.client.force_authenticate(user=self.user1)
        blog_payload = {"title": "Test Post 1", "desc": "This is a test post"}
        new_blog = self.client.post(CREATE_BLOG_URL, blog_payload)
        res = self.client.post(LIKE_URL(new_blog.data["id"]))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        blog = Blog.objects.get(id=new_blog.data["id"])
        users_who_liked = [like.user.username for like in blog.likes.all()]
        self.assertIn(self.user1.username, users_who_liked)

    def test_unlike_blog_with_given_id_successful(self):
        """Test unlike on a blog with given id is successful."""

        self.client.force_authenticate(user=self.user1)
        blog_payload = {"title": "Test Post 1", "desc": "This is a test post"}
        new_blog = self.client.post(CREATE_BLOG_URL, blog_payload)
        res = self.client.post(LIKE_URL(new_blog.data["id"]))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        res = self.client.delete(UNLIKE_URL(new_blog.data["id"]))
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        blog = Blog.objects.get(id=new_blog.data["id"])
        users_who_liked = [like.user.username for like in blog.likes.all()]
        self.assertNotIn(self.user1.username, users_who_liked)

    def test_retrieve_my_blogs_successful(self):
        """Test retrieving blogs of currently logged in user is successful."""

        self.client.force_authenticate(user=self.user1)
        blog_payload = {"title": "Test Post 1", "desc": "This is a test post"}
        new_blog = self.client.post(CREATE_BLOG_URL, blog_payload)
        comment_payload = {"text": "This is a sample comment"}
        comment = self.client.post(COMMENT_URL(new_blog.data["id"]), comment_payload)
        like = self.client.post(LIKE_URL(new_blog.data["id"]))
        res = self.client.get(MY_BLOGS_URL)
        blogs = (
            Blog.objects.filter(author=self.user1.username)
            .all()
            .annotate(likes_count=Count("likes"))
            .order_by("-created_at")
        )
        serializer = BlogWithCommentsSerializer(blogs, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_all_blogs_successful(self):
        """Test retrieving all the blogs is successful."""

        self.client.force_authenticate(user=self.user1)
        blog_payload = {"title": "Test Post 1", "desc": "This is a test post"}
        new_blog = self.client.post(CREATE_BLOG_URL, blog_payload)
        comment_payload = {"text": "This is a sample comment"}
        comment = self.client.post(COMMENT_URL(new_blog.data["id"]), comment_payload)
        like = self.client.post(LIKE_URL(new_blog.data["id"]))
        res = self.client.get(ALL_BLOGS_URL)
        blogs = (
            Blog.objects.all()
            .annotate(likes_count=Count("likes"))
            .order_by("-created_at")
        )
        serializer = BlogWithCommentsSerializer(blogs, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
