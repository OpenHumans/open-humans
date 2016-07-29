from rest_framework import serializers

from activities.data_selfie.models import DataSelfieDataFile
from data_import.models import DataFile

from .models import (DataRequestProject, DataRequestProjectMember,
                     ProjectDataFile)


class ProjectDataSerializer(serializers.ModelSerializer):
    """
    Serialize data for a project.
    """

    class Meta:
        model = DataRequestProject


class DataFileSerializer(serializers.ModelSerializer):
    """
    Serialize a data file.
    """

    download_url = serializers.CharField(source='private_download_url')
    metadata = serializers.JSONField()

    class Meta:
        model = DataFile
        fields = ('id', 'basename', 'created', 'download_url', 'metadata',
                  'source')


class ProjectMemberDataSerializer(serializers.ModelSerializer):
    """
    Serialize data for a project member.
    """

    class Meta:
        model = DataRequestProjectMember

        fields = [
            'created',
            'project_member_id',
            'message_permission',
            'username_shared',
            'sources_shared',
            'username',
            'data',
        ]

    username = serializers.SerializerMethodField()
    data = serializers.SerializerMethodField()

    @staticmethod
    def get_username(obj):
        """
        Only return the username if the user has shared it with the project.
        """
        if obj.username_shared:
            return obj.member.user.username

        return None

    @staticmethod
    def get_data(obj):
        """
        Return the latest data files for each source the user has shared with
        the project.
        """
        files = DataFile.objects.filter(
            user=obj.member.user,
            source__in=obj.sources_shared_including_self)

        files = [data_file for data_file
                 in DataFile.objects.filter(user=obj.member.user)
                 if data_file.source in obj.sources_shared_including_self]

        # TODO_DATAFILE_MANAGEMENT: we get these both above but it's nicer to
        # have the ProjectDataFile vs. the regular DataFile
        project_files = ProjectDataFile.objects.filter(user=obj.member.user)

        if 'data_selfie' in obj.sources_shared:
            files += list(
                DataSelfieDataFile.objects.filter(user=obj.member.user))

        return [DataFileSerializer(data_file).data for data_file in files]
