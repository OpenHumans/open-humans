from django.contrib.auth.models import User
# from django.core.urlresolvers import reverse
from rest_framework import serializers


class ProfileSerializer(serializers.ModelSerializer):
    # url = serializers.SerializerMethodField('get_profile_url')
    message = serializers.SerializerMethodField('get_message')

    class Meta:
        model = User
        # fields = ('id', 'url', 'username')
        fields = ('message',)

    # def get_profile_url(self, obj):
    #     return reverse('member_profile', args=(obj.id,))

    def get_message(self, obj):
        return 'profiles are not yet implemented'
