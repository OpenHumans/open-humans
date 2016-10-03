from rest_framework import serializers

from .models import HuId, UserData


class HuIdSerializer(serializers.ModelSerializer):
    """
    Serializer for a single PGP huID.
    """

    class Meta:  # noqa: D101
        model = HuId
        fields = ('id',)


class UserDataSerializer(serializers.ModelSerializer):
    """
    Serializer for PGP user data.
    """

    class Meta:  # noqa: D101
        model = UserData
        fields = ('id', 'huids')
        read_only_fields = ('ids', 'huids')
