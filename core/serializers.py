from djoser.serializers import UserCreateSerializer

from core.models import User


class MyUserCreateSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = ["id", "email", "username"]

