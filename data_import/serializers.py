from collections import OrderedDict

from rest_framework import serializers

from .models import DataFile


def serialize_data_file_to_dict(data_file):
    """
    Serialze the datafile for storage in logs.
    """
    if not data_file:
        return dict()

    data_file_serializer = DataFileSerializer(data_file).data
    data_file_created = data_file.created.isoformat()
    data_file_serializer["created"] = data_file_created
    data_file_serializer["user_id"] = data_file.user.id
    return data_file_serializer


class DataFileSerializer(serializers.Serializer):
    """
    Serialize a data file.
    """

    class Meta:  # noqa: D101
        model = DataFile

    def to_representation(self, instance):
        """
        Rewrite the ModelSerializer to_representation to pass request on to the
        datafile model's download_url function for logging purposes when
        keys are created.
        """
        request = self.context.get("request", None)
        ret = OrderedDict()
        ret["id"] = instance.id
        ret["basename"] = instance.basename
        ret["created"] = instance.created
        ret["download_url"] = instance.download_url(request)
        ret["metadata"] = instance.metadata
        ret["source"] = instance.source

        return ret
