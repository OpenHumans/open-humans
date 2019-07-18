from django.urls import reverse

from rest_framework import serializers

from common.utils import full_url
from data_import.models import DataFile, DataType
from data_import.serializers import DataFileSerializer

from .models import DataRequestProject, DataRequestProjectMember


class ProjectDataSerializer(serializers.ModelSerializer):
    """
    Publicly available data about a project.
    """

    authorized_members = serializers.ReadOnlyField()
    id_label = serializers.ReadOnlyField()
    type = serializers.ReadOnlyField()
    registered_datatypes = serializers.SerializerMethodField()
    requested_sources = serializers.SerializerMethodField()

    # Note: Legacy, retained to avoid API changes, new field is "requested_sources".
    request_sources_access = serializers.SerializerMethodField()

    class Meta:  # noqa: D101
        model = DataRequestProject
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
            "registered_datatypes",
            "requested_sources",
            "request_sources_access",
            "request_username_access",
            "returned_data_description",
            "short_description",
            "slug",
            "type",
        ]

    def get_requested_sources(self, obj):
        return [
            reverse("api:project", kwargs={"pk": proj.id})
            for proj in obj.requested_sources.all()
        ]

    def get_request_sources_access(self, obj):
        """
        Get the other sources this project requests access to.
        Using a custom function to preserve the existing api
        """
        requested_sources = [source.id_label for source in obj.requested_sources.all()]
        return requested_sources

    def get_registered_datatypes(self, obj):
        """
        Get links to DataType API endpoints for registered DataTypes
        """
        return [
            reverse("api:datatype", kwargs={"pk": dt.id})
            for dt in obj.registered_datatypes.all()
        ]


class ProjectMemberDataSerializer(serializers.ModelSerializer):
    """
    Serialize data for a project member.
    """

    sources_shared = serializers.SerializerMethodField()

    class Meta:  # noqa: D101
        model = DataRequestProjectMember

        fields = [
            "created",
            "project_member_id",
            "file_count",
            "exchange_member",
            "sources_shared",
            "username",
            "data",
        ]

    file_count = serializers.SerializerMethodField()
    exchange_member = serializers.SerializerMethodField()
    username = serializers.SerializerMethodField()
    data = serializers.SerializerMethodField()

    def get_sources_shared(self, obj):
        """
        Get the other sources this project requests access to.
        """
        return [source.id_label for source in obj.granted_sources.all()]

    def get_qs(self, obj):
        """
        Returns a queryset of user's files.
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
        return files

    def get_file_count(self, obj):
        """
        Gets count of files
        """
        files = self.get_qs(obj)
        return files.count()

    def get_exchange_member(self, obj):
        """
        Returns a link to the member exchange endpoint to further retrieve a user's files.
        """
        # Pass through the access token
        access_token = self.context["request"].GET["access_token"]
        exchange_member = reverse("exchange-member")
        return "{0}?project_member_id={1}&access_token={2}".format(
            full_url(exchange_member), obj.project_member_id, access_token
        )

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
        # Limit to the first ten files
        files = self.get_qs(obj)[:10]

        request = self.context.get("request", None)
        return [
            DataFileSerializer(data_file, context={"request": request}).data
            for data_file in files
        ]

    def to_representation(self, obj):
        rep = super().to_representation(obj)

        if not rep["username"]:
            rep.pop("username")

        return rep
