"""
Serializers for the blog API.
"""


from rest_framework import serializers
from blog.models import Blog, Comment, Like


class LikeSerializer(serializers.ModelSerializer):
    """Serializer for the like object"""

    class Meta:
        model = Like
        fields = ["id"]
        read_only_fields = ["id"]


class LikeDetailsSerializer(LikeSerializer):
    """Serializer for like with additional details"""

    class Meta(LikeSerializer.Meta):
        fields = LikeSerializer.Meta.fields + ["user"]


class CommentSerializer(serializers.ModelSerializer):
    """Serializer for the comment object"""

    class Meta:
        model = Comment
        fields = ["id", "text"]
        read_only_fields = ["id"]


class CommentDetailsSerializer(CommentSerializer):
    """Serializer for comment with additional details"""

    class Meta(CommentSerializer.Meta):
        fields = CommentSerializer.Meta.fields + ["user"]


class BlogSerializer(serializers.ModelSerializer):
    """Serializer for the blog object"""

    class Meta:
        model = Blog
        fields = ["id", "title", "desc", "created_at"]
        read_only_fields = ["id"]


class BlogWithCommentsSerializer(BlogSerializer):
    """Serializer for the blog with additional details"""

    likes = LikeDetailsSerializer(many=True)
    comments = CommentDetailsSerializer(many=True)
    likes_count = serializers.IntegerField()

    class Meta(BlogSerializer.Meta):
        fields = BlogSerializer.Meta.fields + [
            "author",
            "likes",
            "likes_count",
            "comments",
        ]
