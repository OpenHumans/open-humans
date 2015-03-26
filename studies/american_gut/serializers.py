from rest_framework import serializers

from .models import Barcode, UserData


class BarcodeSerializer(serializers.ModelSerializer):
    """
    Serializer for a single American Gut barcode.
    """

    class Meta:
        model = Barcode
        fields = ('value',)


class UserDataSerializer(serializers.ModelSerializer):
    """
    Serializer for American Gut user data.
    """

    class Meta:
        model = UserData
        fields = ('id', 'barcodes')
