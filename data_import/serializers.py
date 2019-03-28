from collections import OrderedDict

from rest_framework import serializers

from private_sharing.models import DataRequestProject

from .models import DataFile, DataType


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


class DataTypeSerializer(serializers.ModelSerializer):
    """
    Serialize DataTypes
    """

    class Meta:  # noqa: D101
        model = DataType

        fields = ["id", "name", "parent", "description", "source_projects"]

    source_projects = serializers.SerializerMethodField()

    def get_source_projects(self, obj):
        """
        Get projects associated with a datatype
        """
        projects = DataRequestProject.objects.filter(
            registered_datatypes=obj
        ).distinct()
        return [project.id_label for project in projects]
