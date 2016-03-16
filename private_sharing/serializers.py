from rest_framework import serializers

from .models import DataRequestProject


class ProjectDataSerializer(serializers.ModelSerializer):
    """
    Serialize data for a project.
    """

    class Meta:
        model = DataRequestProject
