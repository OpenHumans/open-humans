from django.contrib.auth.models import User
# from django.core.urlresolvers import reverse
from rest_framework import serializers


class MemberSerializer(serializers.ModelSerializer):
    """
    Serialize a member profile.
    """
    # url = serializers.SerializerMethodField('get_profile_url')
    message = serializers.SerializerMethodField()

    class Meta:
        model = User
        # fields = ('id', 'url', 'username')
        fields = ('message',)

    # def get_profile_url(self, obj):
    #     return reverse('member_profile', args=(obj.id,))

    @staticmethod
    def get_message(obj):
        return ('the call was successful but profiles do not contain data at '
                'present')
