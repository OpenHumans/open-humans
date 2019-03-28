from collections import OrderedDict

from rest_framework import serializers

from .models import DataFile


def serialize_datafile_to_dict(datafile):
    """
    Serialize the datafile for storage in logs.
    """
    if not datafile:
        return dict()

    datafile_serializer = DataFileSerializer(datafile).data
    datafile_created = datafile.created.isoformat()
    datafile_serializer["created"] = datafile_created
    datafile_serializer["user_id"] = datafile.user.id
    return datafile_serializer


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
