"""
Models for the blog API.
"""


from django.db import models
from user.models import User


class Blog(models.Model):
    """Blog object"""

    title = models.CharField(max_length=255)
    desc = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)


class Comment(models.Model):
    """Comment object"""

    text = models.TextField()
    blog = models.ForeignKey(
        Blog, on_delete=models.CASCADE, related_name="comments", db_index=True
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True)


class Like(models.Model):
    """Like object"""

    blog = models.ForeignKey(
        Blog, on_delete=models.CASCADE, related_name="likes", db_index=True
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True)
