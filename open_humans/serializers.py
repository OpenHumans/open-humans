from collections import OrderedDict

from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse

from rest_framework import serializers
from rest_framework.fields import SerializerMethodField

from private_sharing.models import (
    DataRequestProject,
    DataRequestProjectMember,
    id_label_to_project,
    project_membership_visible,
)


class MemberSerializer(serializers.ModelSerializer):
    """
    Serialize a member profile.
    """

    url = serializers.SerializerMethodField("get_profile_url")
    name = serializers.CharField(source="member.name")

    class Meta:  # noqa: D101
        model = get_user_model()
        fields = ("id", "name", "url", "username")

    @staticmethod
    def get_profile_url(obj):
        return reverse("member-detail", kwargs={"slug": obj.username})


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
