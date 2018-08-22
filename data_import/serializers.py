from rest_framework import serializers

from .models import DataFile, RemovedData


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

class RemovedDataSerializer(serializers.ModelSerializer):
    """
    Serialize removed data.
    """

    class Meta:
        model = RemovedData
        fields = ('id', 'date', 'member_id', 'file_url', 'source')
