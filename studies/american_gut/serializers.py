from rest_framework import serializers

from .models import UserData


class UserDataSerializer(serializers.ModelSerializer):
    """
    Serializer for American Gut user data.
    """

    data = serializers.JSONField()

    class Meta:
        model = UserData
        fields = ('id', 'barcodes', 'data')
        read_only_fields = ('id', 'barcodes')
