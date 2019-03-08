from rest_framework import serializers

from data_import.models import DataFile, DataType
from data_import.serializers import DataFileSerializer

from .models import DataRequestProject, DataRequestProjectMember


class ProjectDataSerializer(serializers.ModelSerializer):
    """
    Serialize data for a project.
    """

    # Note: Old name kept to avoid API changes, field is now "requested_sources".
    request_sources_access = serializers.SerializerMethodField()

    class Meta:  # noqa: D101
        model = DataRequestProject

        authorized_members = serializers.Field()
        id_label = serializers.Field()
        type = serializers.Field()

        fields = [
            "active",
            "approved",
            "authorized_members",
            "badge_image",
            "contact_email",
            "id",
            "id_label",
            "info_url",
            "is_academic_or_nonprofit",
            "is_study",
            "leader",
            "long_description",
            "name",
            "organization",
            "request_sources_access",
            "request_username_access",
            "returned_data_description",
            "short_description",
            "slug",
            "type",
        ]

    def get_request_sources_access(self, obj):
        """
        Get the other sources this project requests access to.
        Using a custom function to preserve the existing api
        """
        requested_sources = [source.id_label for source in obj.requested_sources.all()]
        return requested_sources


class ProjectMemberDataSerializer(serializers.ModelSerializer):
    """
    Serialize data for a project member.
    """

    sources_shared = serializers.SerializerMethodField()

    class Meta:  # noqa: D101
        model = DataRequestProjectMember

        fields = ["created", "project_member_id", "sources_shared", "username", "data"]

    username = serializers.SerializerMethodField()
    data = serializers.SerializerMethodField()

    def get_sources_shared(self, obj):
        """
        Get the other sources this project requests access to.
        """
        return [source.id_label for source in obj.granted_sources.all()]

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
        all_files = DataFile.objects.filter(user=obj.member.user).exclude(
            parent_project_data_file__completed=False
        )
        if obj.all_sources_shared:
            files = all_files
        else:
            sources_shared = self.get_sources_shared(obj)
            sources_shared.append(obj.project.id_label)
            files = all_files.filter(source__in=sources_shared)
        request = self.context.get("request", None)
        request.public_sources = list(
            obj.member.public_data_participant.publicdataaccess_set.filter(
                is_public=True
            ).values_list("data_source", flat=True)
        )
        return [
            DataFileSerializer(data_file, context={"request": request}).data
            for data_file in files
        ]

    def to_representation(self, obj):
        rep = super().to_representation(obj)

        if not rep["username"]:
            rep.pop("username")

        return rep


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
        projects = DataRequestProject.objects.filter(datatypes=obj).distinct()
        return [project.id_label for project in projects]
