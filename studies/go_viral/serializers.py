from rest_framework import serializers

from .models import UserData


class UserDataSerializer(serializers.ModelSerializer):
    """
    Serializer for GoViral user data.
    """

    class Meta:  # noqa: D101
        model = UserData
        fields = ('id', 'data')
        read_only_fields = ('id',)
