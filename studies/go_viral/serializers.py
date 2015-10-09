from rest_framework import serializers

from .models import GoViralId, UserData


class GoViralIdSerializer(serializers.ModelSerializer):
    """
    Serializer fro a single GoViral user ID.
    """

    class Meta:
        model = GoViralId
        fields = ('value',)


class UserDataSerializer(serializers.ModelSerializer):
    """
    Serializer for GoViral user data.
    """

    class Meta:
        model = UserData
        fields = ('id', 'go_viral_ids')
        read_only_fields = ('id', 'go_viral_ids')
