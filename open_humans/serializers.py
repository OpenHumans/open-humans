from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import serializers
from rest_framework.fields import SerializerMethodField

from private_sharing.models import project_membership_visible
from private_sharing.utilities import (
    get_source_labels_and_names_including_dynamic)


class MemberSerializer(serializers.ModelSerializer):
    """
    Serialize a member profile.
    """

    url = serializers.SerializerMethodField('get_profile_url')
    name = serializers.CharField(source='member.name')

    class Meta:  # noqa: D101
        model = get_user_model()
        fields = ('id', 'name', 'url', 'username')

    @staticmethod
    def get_profile_url(obj):
        return reverse('member-detail', kwargs={'slug': obj.username})


class MemberDataSourcesSerializer(serializers.ModelSerializer):
    """
    Serialize the sources of a user.
    """

    sources = SerializerMethodField()

    class Meta:  # noqa: D101
        model = get_user_model()
        fields = ('username', 'sources')

    @staticmethod
    def get_sources(obj):
        if not hasattr(obj, 'member'):
            return []

        sources = (k for k, i in get_source_labels_and_names_including_dynamic()
                   if project_membership_visible(obj.member, k))
        return sorted(sources)
