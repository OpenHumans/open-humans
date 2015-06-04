from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from rest_framework import serializers


class MemberSerializer(serializers.ModelSerializer):
    """
    Serialize a member profile.
    """

    url = serializers.SerializerMethodField('get_profile_url')

    class Meta:
        model = get_user_model()
        fields = ('id', 'url', 'username')

    @staticmethod
    def get_profile_url(obj):
        return reverse('member-detail', args=(obj.username,))
