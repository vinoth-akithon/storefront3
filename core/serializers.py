from djoser.serializers import \
    (UserCreateSerializer as BaseUserCreateSerializer,
     UserCreatePasswordRetypeSerializer as BaseUserCreatePasswordRetypeSerializer)
from djoser.serializers import UserSerializer
from rest_framework import serializers


class UserCreateSerializer(BaseUserCreateSerializer):
    class Meta(BaseUserCreateSerializer.Meta):
        fields = ["id", "username", "password",
                  "email", "first_name", "last_name"]


class UserCreatePasswordRetypeSerializer(BaseUserCreatePasswordRetypeSerializer):
    re_password = serializers.EmailField(write_only=True)

    class Meta(BaseUserCreateSerializer.Meta):
        fields = ["id", "username", "password", "re_password",
                  "email", "first_name", "last_name"]


class UserRetriveSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        fields = ["id", "email", "username", "first_name", "last_name"]
