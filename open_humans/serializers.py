from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from rest_framework import serializers

# TODO: Change to MemberSerializer and get_member_url?
class ProfileSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField('get_profile_url')

    class Meta:
        model = User
        fields = ('id', 'url', 'username')

    def get_profile_url(self, obj):
        return reverse('member-detail', args=(obj.id,))
