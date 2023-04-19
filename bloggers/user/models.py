"""
Models for the user API.
"""

from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)


class UserManager(BaseUserManager):
    """Manager for users"""

    def create_user(self, email, password=None, **extra_fields):
        """Create, save and return a new user"""

        endIndex = email.rfind("@")
        username = email[0:endIndex]
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """User object"""

    username = models.CharField(max_length=255, primary_key=True)
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "username"


class Follow(models.Model):
    """Follow object"""

    follower = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="following", db_index=True
    )
    following = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="follower", db_index=True
    )
