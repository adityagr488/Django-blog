"""
Serializers for the user API.
"""


from rest_framework import serializers
from user.models import User, Follow


class FollowSerializer(serializers.ModelSerializer):
    """Serializer for the follow object"""

    class Meta:
        model = Follow
        fields = ["id"]
        read_only_fields = ["id"]


class FollowerSerializer(FollowSerializer):
    """Serializer for the user following"""

    class Meta(FollowSerializer.Meta):
        fields = FollowSerializer.Meta.fields + ["following"]


class FollowingSerializer(FollowSerializer):
    """Serializer for the user followers"""

    class Meta(FollowSerializer.Meta):
        fields = FollowSerializer.Meta.fields + ["follower"]


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the user object"""

    class Meta:
        model = User
        fields = ["username", "email", "password", "name"]
        extra_kwargs = {
            "username": {"read_only": True},
            "password": {"write_only": True},
        }

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class UserDetailsSerializer(UserSerializer):
    """Serializer for the user details"""

    follower = FollowingSerializer(many=True)
    following = FollowerSerializer(many=True)

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ["follower", "following"]
