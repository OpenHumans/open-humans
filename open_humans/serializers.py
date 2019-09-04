from collections import OrderedDict

from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse

from rest_framework import serializers
from rest_framework.fields import SerializerMethodField

from common.utils import full_url
from data_import.models import DataFile
from private_sharing.models import (
    DataRequestProject,
    DataRequestProjectMember,
    id_label_to_project,
    project_membership_visible,
)
from private_sharing.serializers import ProjectDataSerializer

from .models import Member

User = get_user_model()


class PublicProjectSerializer(ProjectDataSerializer):
    """
    Serialize publicly available project information.
    """

    pass


class PublicMemberSerializer(serializers.ModelSerializer):
    """
    Serialize a member profile.
    """

    profile_url = serializers.SerializerMethodField()
    username = serializers.CharField(source="user.username")

    class Meta:  # noqa: D101
        model = Member
        fields = ("name", "profile_url", "username")

    @staticmethod
    def get_profile_url(obj):
        return full_url(reverse("member-detail", kwargs={"slug": obj.user.username}))


class PublicDataFileSerializer(serializers.ModelSerializer):
    """
    Serialize a public data file.
    """

    class Meta:  # noqa: D101
        model = DataFile
        fields = (
            "id",
            "basename",
            "created",
            "datatypes",
            "download_url",
            "metadata",
            "source_project",
            "user",
        )

    metadata = serializers.JSONField()
    datatypes = serializers.SerializerMethodField("get_file_datatypes")
    source_project = serializers.SerializerMethodField()

    def get_file_datatypes(self, obj):
        """
        Get links to DataType API endpoints for file DataTypes
        """
        return [
            full_url(reverse("api:datatype", kwargs={"pk": dt.id}))
            for dt in obj.datatypes.all()
        ]

    def get_source_project(self, obj):
        return full_url(
            reverse("api:project", kwargs={"pk": obj.direct_sharing_project.id})
        )

    def to_representation(self, data):
        """
        Override to get download link, remove user information if hidden membership.
        """
        rep = super().to_representation(data)

        membership_visible = project_membership_visible(data.user.member, data.source)

        # If shared with membership hidden, don't leak info via username filter!
        usernames = self.context["request"].query_params.get("username", [])
        if (data.user.username in usernames) and not membership_visible:
            return OrderedDict()

        if not membership_visible:
            rep["user"] = {"id": None, "name": None, "username": None}
        else:
            rep["user"] = {
                "id": data.user.member.id,
                "name": data.user.member.name,
                "username": data.user.username,
            }

        # This is actually a method; we need to use it to get the link.
        rep["download_url"] = data.download_url(self.context["request"])

        return rep


#####################################################################
# LEGACY SERIALIZERS
#
# The following serializers are used by deprecated API endpoints.
#####################################################################


class MemberDataSourcesSerializer(serializers.ModelSerializer):
    """
    Serialize the sources of a user.
    """

    sources = SerializerMethodField()

    class Meta:  # noqa: D101
        model = get_user_model()
        fields = ("username", "sources")

    @staticmethod
    def get_sources(obj):
        if not hasattr(obj, "member"):
            return []
        projects = DataRequestProject.objects.filter(
            approved=True, no_public_data=False
        ).exclude(returned_data_description="")
        sources = []
        for project in projects:
            if project_membership_visible(obj.member, project.id_label):
                if not project.no_public_data:
                    sources.append(project.id_label)
        return sorted(sources)


class NoNullSerializer(serializers.ListSerializer):
    """
    Override ListSerializer's to_representation.
    """

    def to_representation(self, data):
        """
        List of object instances -> List of dicts of primitive datatypes.
        Overrides ListSerializer to add for checking for empty items.
        """
        # Dealing with nested relationships, data can be a Manager,
        # so, first get a queryset from the Manager if needed
        iterable = data.all() if isinstance(data, models.Manager) else data

        ret = []
        for item in iterable:
            repres = self.child.to_representation(item)
            if repres != OrderedDict():
                ret = ret + [repres]
        return ret


class DataUsersBySourceSerializer(serializers.ModelSerializer):
    """
    Serialize the members of a data source.
    """

    class Meta:  # noqa: D101
        model = DataRequestProjectMember
        fields = ("id", "project", "visible")
        list_serializer_class = NoNullSerializer

    def to_representation(self, data):
        ret = OrderedDict()
        fields = self.get_fields()
        query_params = dict(self.context.get("request").query_params)
        if "source" in query_params:
            source = query_params["source"][0]
        else:
            source = "direct-sharing-{}".format(str(getattr(data, "id")))

        project = id_label_to_project(source)
        if getattr(data, "id") != project.id:
            return ret
        queryset = DataRequestProject.objects.filter(id=project.id)
        usernames = list(
            queryset.get()
            .project_members.filter(
                joined=True, authorized=True, revoked=False, visible=True
            )
            .values_list("member__user__username", flat=True)
        )
        ret["source"] = source
        ret["name"] = getattr(data, "name")
        ret["usernames"] = usernames
        return ret
