from rest_framework import serializers

from data_import.models import DataRetrievalTask

from .models import DataRequestProject, DataRequestProjectMember


class ProjectDataSerializer(serializers.ModelSerializer):
    """
    Serialize data for a project.
    """

    class Meta:
        model = DataRequestProject


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
        tasks = (DataRetrievalTask.objects
                 .for_user(obj.member.user)
                 .grouped_recent())

        return {
            key: [data_file.file.url for data_file in value.datafiles.all()]
            for key, value in tasks.items()
            if key in obj.sources_shared
        }
