from collections import OrderedDict

from rest_framework import serializers
from rest_framework.relations import PKOnlyObject

from .models import DataFile


class DataFileSerializer(serializers.ModelSerializer):
    """
    Serialize a data file.
    """

    metadata = serializers.JSONField()

    class Meta:  # noqa: D101
        model = DataFile
        fields = ('id', 'basename', 'created', 'download_url', 'metadata',
                  'source')

    def to_representation(self, instance):
        """
        Rewrite the ModelSerializer to_representation to pass request on to the
        datafile model's private_download_url function for logging purposes when
        keys are created.
        """
        ret = OrderedDict()
        fields = self._readable_fields
        for field in fields:
            attribute = field.get_attribute(instance)

            check_for_none = attribute.pk if isinstance(
                attribute, PKOnlyObject) else attribute
            if check_for_none is None:
                ret[field.field_name] = None
            else:
                if field.field_name == 'download_url':
                    ret[field.field_name] = instance.private_download_url(
                        self.context.get('request', None))
                else:
                    ret[field.field_name] = field.to_representation(attribute)

        return ret
