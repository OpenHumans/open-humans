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

        authorized_members = serializers.Field()
        id_label = serializers.Field()
        type = serializers.Field()

        fields = [
            'active',
            'approved',
            'authorized_members',
            'badge_image',
            'contact_email',
            'id',
            'id_label',
            'info_url',
            'is_academic_or_nonprofit',
            'is_study',
            'leader',
            'long_description',
            'name',
            'organization',
            'request_sources_access',
            'request_username_access',
            'returned_data_description',
            'short_description',
            'slug',
            'type',
        ]


class ProjectMemberDataSerializer(serializers.ModelSerializer):
    """
    Serialize data for a project member.
    """

    class Meta:  # noqa: D101
        model = DataRequestProjectMember

        fields = [
            'created',
            'project_member_id',
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

    def get_data(self, obj):
        """
        Return current data files for each source the user has shared with
        the project, including the project itself.
        """
        all_files = DataFile.objects.filter(
            user=obj.member.user).exclude(
                parent_project_data_file__completed=False)
        if obj.all_sources_shared:
            files = all_files
        else:
            files = all_files.filter(
                source__in=obj.sources_shared_including_self)
        request = self.context.get('request', None)
        request.public_sources = (obj.member.public_data_participant
                          .publicdataaccess_set
                          .filter(is_public=True))
        return [DataFileSerializer(data_file, context={'request': request}).data
                for data_file in files]

    def to_representation(self, obj):
        rep = super().to_representation(obj)

        if not rep['username']:
            rep.pop('username')

        return rep
