from collections import OrderedDict

from rest_framework import serializers

from data_import.models import DataFile
from open_humans.models import User
from private_sharing.models import project_membership_visible


class PublicDataFileSerializer(serializers.ModelSerializer):
    """
    Serialize a public data file.
    """

    metadata = serializers.JSONField()

    def to_representation(self, data):
        ret = OrderedDict()
        fields = self.get_fields()
        query_params = dict(self.context.get('request').query_params)
        source = getattr(data, 'source')
        user_t = getattr(data, 'user')
        usernames = []
        if 'username' in query_params:
            usernames = query_params['username']
        visible = project_membership_visible(user_t.member, source)
        if (user_t.username in usernames) and not visible:
            return ret
        for field in fields:
            item = getattr(data, str(field))
            if isinstance(item, User):
                if visible:
                    member = getattr(user_t, 'member')
                    user = {
                        "id": getattr(member, 'member_id'),
                        "name": getattr(member, 'name'),
                        "username": getattr(item, 'username'),
                    }
                else:
                    user = {"id": None, "name": None, "username": None}
                ret['user'] = user
            else:
                ret[str(field)] = getattr(data, field)
        return ret

    class Meta:  # noqa: D101
        model = DataFile
        fields = (
            'id',
            'basename',
            'created',
            'download_url',
            'metadata',
            'source',
            'user',
        )
