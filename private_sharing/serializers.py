from django.urls import reverse

from rest_framework import serializers

from common.utils import full_url
from data_import.models import DataFile, DataType
from data_import.serializers import DataFileSerializer

from .models import (
    DataRequestProject,
    DataRequestProjectMember,
    OAuth2DataRequestProject,
)


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


class ProjectCreationSerializer(serializers.Serializer):
    """
    Fields that we should be getting through the API:
    name
    long_description

    Remainder of required fields; these are set at save() in the view.
    is_study:  set to False
    leader:  set to member.name from oauth2 token
    coordinator:  get from oauth2 token
    is_academic_or_nonprofit: False
    add_data:  false
    explore_share:  false
    short_description:  first 139 chars of long_description plus an elipse
    active:  True
    coordinator:  from oauth2 token
    """

    name = serializers.CharField(max_length=100)
    long_description = serializers.CharField(max_length=1000)

    def create(self, validated_data):
        """
        Returns a new OAuth2DataRequestProject
        """
        return OAuth2DataRequestProject.objects.create(validated_data)

    def validate_name(self, value):
        """
        Check the name
        """
        if value:
            return value
        raise serializers.ValidationError("Please provide a name")

    def validate_long_description(self, value):
        """
        Check the description
        """
        if value:
            return value
        raise serializers.ValidationError("Please provide a Description")
