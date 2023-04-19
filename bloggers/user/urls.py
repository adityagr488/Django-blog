"""
URL mappings for the user API.
"""

from django.urls import path
from user import views as user_view

app_name = "user"

urlpatterns = [
    path("", user_view.CreateUserView.as_view(), name="create-user"),
    path("/me", user_view.UserView.as_view(), name="me"),
    path("/follow/<str:username>", user_view.FollowView().as_view(), name="follow"),
    path(
        "/unfollow/<str:username>", user_view.UnFollowView().as_view(), name="unfollow"
    ),
]
