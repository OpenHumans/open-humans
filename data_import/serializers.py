from collections import OrderedDict

from rest_framework import serializers

from .models import DataFile


class DataFileSerializer(serializers.ModelSerializer):
    """
    Serialize a data file.
    """

    download_url = serializers.CharField(source='private_download_url')
    metadata = serializers.JSONField()

    class Meta:  # noqa: D101
        model = DataFile
        fields = ('id', 'basename', 'created', 'download_url', 'metadata',
                  'source')
