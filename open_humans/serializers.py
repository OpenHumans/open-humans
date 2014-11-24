from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from rest_framework import serializers


class ProfileSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField('get_profile_url')

    class Meta:
        model = User
        fields = ('id', 'url', 'username')

    def get_profile_url(self, obj):
        return reverse('member_profile', args=(obj.id,))
