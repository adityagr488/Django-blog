"""
Views for the user object.
"""

from rest_framework import generics, permissions, status, response
from rest_framework_simplejwt.authentication import JWTAuthentication
from user.serializers import UserSerializer, UserDetailsSerializer, FollowSerializer
from user.models import User, Follow


class CreateUserView(generics.CreateAPIView):
    """Create new user"""

    serializer_class = UserSerializer


class UserView(generics.RetrieveAPIView):
    """Retrieve current user"""

    serializer_class = UserDetailsSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class FollowView(generics.CreateAPIView):
    """Follow user with given username"""

    serializer_class = FollowSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    queryset = User.objects.all()
    lookup_url_kwarg = "username"

    def post(self, request, *args, **kwargs):
        already_following = Follow.objects.filter(
            follower=request.user, following=self.get_object()
        ).exists()
        if not already_following:
            Follow.objects.create(follower=request.user, following=self.get_object())
        return response.Response(status=status.HTTP_201_CREATED)


class UnFollowView(generics.DestroyAPIView):
    """Unfollow user with given username"""

    serializer_class = FollowSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    queryset = User.objects.all()
    lookup_url_kwarg = "username"

    def delete(self, request, *args, **kwargs):
        Follow.objects.filter(
            follower=request.user, following=self.get_object()
        ).delete()
        return response.Response(status=status.HTTP_204_NO_CONTENT)
