from rest_framework import serializers

from .models import UserData


# TODO: this could be used for American Gut as well
class UserDataSerializer(serializers.ModelSerializer):
    """
    Serializer for Wildlife of Our Home user data.
    """

    # DictField works for JSON with an object at the root
    data = serializers.DictField()

    class Meta:
        model = UserData
        fields = ('id', 'data')
        read_only_fields = ('id')
