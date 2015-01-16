from rest_framework import serializers

from .models import HuId, UserData


class HuIdSerializer(serializers.ModelSerializer):
    class Meta:
        model = HuId
        fields = ('value',)


class UserDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserData
        fields = ('id', 'huids')
