from collections import OrderedDict

from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import serializers
from rest_framework.fields import SerializerMethodField

from private_sharing.models import DataRequestProject, id_label_to_project, project_membership_visible
from private_sharing.utilities import (
    get_source_labels_and_names_including_dynamic)


def using_badges_to_track_project_membership_must_die(source):
    """
    Right now we are using badges to track project membership.  This here
    function returns a list of usernames that are members of a given project
    based on their badges.
    """
    UserModel = get_user_model()
    users = UserModel.objects.filter(is_active=True)
    usernames = []
    for user in users:
        try:
            getattr(user, 'member')
        except AttributeError:
            continue
        for badge in user.member.badges:
            if 'label' not in badge:
                continue

            if badge['label'] == source:
                if project_membership_visible(user.member, source):
                    usernames.append(getattr(user, 'username'))

    return usernames


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


class DataUsersBySourceSerializer(serializers.ModelSerializer):
    """
    Serialize the members of a data source.
    """

    class Meta:  # noqa: D101
        model = DataRequestProject
        fields = ('id', 'name')

    def to_representation(self, data):
        ret = OrderedDict()
        fields = self.get_fields()
        query_params = dict(self.context.get('request').query_params)
        source = 'direct-sharing-{}'.format(str(getattr(data, 'id')))
        usernames = using_badges_to_track_project_membership_must_die(source)

        ret['source'] = source
        ret['name'] = getattr(data, 'name')
        ret['usernames'] = usernames
        return ret
