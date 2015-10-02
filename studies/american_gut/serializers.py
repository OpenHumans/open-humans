from rest_framework import serializers

from .models import Barcode, SurveyId, UserData


class BarcodeSerializer(serializers.ModelSerializer):
    """
    Serializer for a single American Gut barcode.
    """

    class Meta:
        model = Barcode
        fields = ('value',)


class SurveyIdSerializer(serializers.ModelSerializer):
    """
    Serializer for a single American Gut survey ID.
    """

    class Meta:
        model = SurveyId
        fields = ('value',)


class UserDataSerializer(serializers.ModelSerializer):
    """
    Serializer for American Gut user data.
    """

    class Meta:
        model = UserData
        fields = ('id', 'barcodes')
