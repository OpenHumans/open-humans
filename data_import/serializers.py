from collections import OrderedDict

from rest_framework import serializers

from .models import AWSDataFileAccessLog, DataFile, NewDataFileAccessLog


def serialize_datafile_to_dict(datafile):
    """
    Serialize the datafile for storage in logs.
    """
    if not datafile:
        return dict()

    serialized_datafile = DataFileSerializer(datafile).data
    datafile_created = datafile.created.isoformat()
    serialized_datafile["created"] = datafile_created
    serialized_datafile["user_id"] = datafile.user.id
    return serialized_datafile


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


class NewDataFileAccessLogSerializer(serializers.ModelSerializer):
    """
    Serialize the logs of file access events from Open Human's end.
    """

    user = serializers.IntegerField(source="user.id")
    datafile = serializers.JSONField(source="serialized_data_file")
    key = serializers.JSONField(source="data_file_key")

    class Meta:  # noqa: D101
        model = NewDataFileAccessLog
        fields = ["date", "ip_address", "user", "datafile", "key", "aws_url"]


class AWSDataFileAccessLogSerializer(serializers.ModelSerializer):
    """
    Serialize the logs of file access events from Amazon's end.
    """

    datafile = serializers.JSONField(source="serialized_data_file")

    class Meta:  # noqa: D101
        model = AWSDataFileAccessLog
        fields = [
            "time",
            "remote_ip",
            "request_id",
            "operation",
            "bucket_key",
            "request_uri",
            "status",
            "bytes_sent",
            "object_size",
            "total_time",
            "turn_around_time",
            "referrer",
            "user_agent",
            "cipher_suite",
            "host_header",
            "datafile",
        ]
