from django.contrib.auth import get_user_model
from rest_framework import serializers

from data_import.models import DataFile


class UserSerializer(serializers.ModelSerializer):
    """
    Serialize a user to a representation that's useful for people looking at
    public DataFiles.
    """

    id = serializers.SlugRelatedField(source='member', read_only=True,
                                      slug_field='member_id')

    name = serializers.SlugRelatedField(source='member', read_only=True,
                                        slug_field='name')

    class Meta:  # noqa: D101
        model = get_user_model()
        fields = ('id', 'name', 'username')


class PublicDataFileSerializer(serializers.ModelSerializer):
    """
    Serialize a public data file.
    """

    metadata = serializers.JSONField()
    user = UserSerializer()

    class Meta:  # noqa: D101
        model = DataFile
        fields = ('id', 'basename', 'created', 'download_url', 'metadata',
                  'source', 'user')
