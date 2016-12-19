from rest_framework import serializers

from data_import.models import DataFile
from data_import.serializers import DataFileSerializer

from .models import DataRequestProject, DataRequestProjectMember


class ProjectDataSerializer(serializers.ModelSerializer):
    """
    Serialize data for a project.
    """

    class Meta:  # noqa: D101
        model = DataRequestProject


class ProjectMemberDataSerializer(serializers.ModelSerializer):
    """
    Serialize data for a project member.
    """

    class Meta:  # noqa: D101
        model = DataRequestProjectMember

        fields = [
            'created',
            'project_member_id',
            'message_permission',
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
        Return current data files for each source the user has shared with
        the project, including the project itself.
        """
        files = DataFile.objects.filter(
            user=obj.member.user,
            source__in=obj.sources_shared_including_self).exclude(
            parent_project_data_file__completed=False).current()

        return [DataFileSerializer(data_file).data for data_file in files]

    def to_representation(self, obj):
        rep = super(ProjectMemberDataSerializer, self).to_representation(obj)

        if not rep['username']:
            rep.pop('username')

        return rep
