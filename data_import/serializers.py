from collections import OrderedDict

from rest_framework import serializers

from .models import DataFile


class DataFileSerializer(serializers.Serializer):
    """
    Serialize a data file.
    """

    class Meta:  # noqa: D101
        model = DataFile

    def to_representation(self, instance):
        """
        Rewrite the ModelSerializer to_representation to pass request on to the
        datafile model's private_download_url function for logging purposes when
        keys are created.
        """
        ret = OrderedDict()
        fields = ['id', 'basename', 'created', 'download_url', 'metadata', 'source']
        for field in fields:
            if field == 'download_url':
                ret[field] = instance.private_download_url(
                    self.context.get('request', None)
                )
            else:
                ret[field] = getattr(instance, field)

        return ret
