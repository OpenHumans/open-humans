from rest_framework import serializers

from .models import HuId, UserData


class HuIdSerializer(serializers.ModelSerializer):
    """
    Serializer for a single PGP huID.
    """

    class Meta:
        model = HuId
        fields = ('value',)


class UserDataSerializer(serializers.ModelSerializer):
    """
    Serializer for PGP user data.
    """

    class Meta:
        model = UserData
        fields = ('id', 'huids')
