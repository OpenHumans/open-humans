from rest_framework import serializers

from .models import GoViralId, UserData


class GoViralIdSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoViralId
        fields = ('value',)


class UserDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserData
        fields = ('id', 'go_viral_ids')
