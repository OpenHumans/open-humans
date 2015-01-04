from django.contrib.auth.models import User
# from django.core.urlresolvers import reverse
from rest_framework import serializers

# TODO: Change to MemberSerializer and get_member_url?
class ProfileSerializer(serializers.ModelSerializer):
    # url = serializers.SerializerMethodField('get_profile_url')
    message = serializers.SerializerMethodField()

    class Meta:
        model = User
        # fields = ('id', 'url', 'username')
        fields = ('message',)

    # def get_profile_url(self, obj):
    #     return reverse('member_profile', args=(obj.id,))

    def get_message(self, obj):
        return ('the call was successful but profiles do not contain data at '
                'present')
