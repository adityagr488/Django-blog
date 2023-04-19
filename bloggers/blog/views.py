"""
Views for the blog API.
"""

from django.db.models import Count
from rest_framework import generics, permissions, response, status
from rest_framework_simplejwt.authentication import JWTAuthentication
from blog.serializers import (
    BlogSerializer,
    BlogWithCommentsSerializer,
    CommentSerializer,
    LikeSerializer,
)
from blog.models import Blog, Like


class BlogView(generics.CreateAPIView):
    """Create new blog"""

    serializer_class = BlogSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class BlogWithCommentsView(generics.RetrieveDestroyAPIView):
    """Retrieve and Delete blog"""

    serializer_class = BlogWithCommentsSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    queryset = Blog.objects.annotate(likes_count=Count("likes"))
    lookup_url_kwarg = "id"

    def perform_destroy(self, instance):
        instance.delete()


class AllBlogsView(generics.ListAPIView):
    """Retrieve all blogs"""

    serializer_class = BlogWithCommentsSerializer
    queryset = Blog.objects.annotate(likes_count=Count("likes")).order_by("-created_at")

    def get_queryset(self):
        return self.queryset.order_by("-created_at")


class MyBlogsView(AllBlogsView):
    """Retrieve blogs of logged in user"""

    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(author=self.request.user).order_by("-created_at")


class CommentView(generics.CreateAPIView):
    """Create new comment on a blog"""

    serializer_class = CommentSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    queryset = Blog.objects.all()
    lookup_url_kwarg = "id"

    def perform_create(self, serializer):
        serializer.save(blog=self.get_object(), user=self.request.user)


class LikeView(generics.CreateAPIView):
    """Like a blog"""

    serializer_class = LikeSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    queryset = Blog.objects.all()
    lookup_url_kwarg = "id"

    def post(self, request, *args, **kwargs):
        already_liked = Like.objects.filter(
            blog=self.get_object(), user=self.request.user
        ).exists()
        if not already_liked:
            Like.objects.create(blog=self.get_object(), user=self.request.user)
        return response.Response(status=status.HTTP_200_OK)


class UnLikeView(generics.DestroyAPIView):
    """Unlike a blog"""

    serializer_class = LikeSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    queryset = Blog.objects.all()
    lookup_url_kwarg = "id"

    def delete(self, request, *args, **kwargs):
        Like.objects.filter(blog=self.get_object(), user=self.request.user).delete()
        return response.Response(status=status.HTTP_204_NO_CONTENT)
