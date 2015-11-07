# from django.core.urlresolvers import reverse
from rest_framework import serializers

from .models import PublicDataAccess


# TODO: Add serializer for DataFiles that uses duck-typing

class PublicDataSerializer(serializers.ModelSerializer):
    """
    Serialize a public data file.
    """

    class Meta:
        model = PublicDataAccess
        fields = ('id', 'download_url')
