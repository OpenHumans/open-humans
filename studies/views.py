from django.apps import apps
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.views.generic.base import TemplateView

from private_sharing.utilities import source_to_url_slug
from rest_framework.generics import (ListCreateAPIView, RetrieveAPIView,
                                     RetrieveUpdateAPIView,
                                     RetrieveUpdateDestroyAPIView)

from common.mixins import NeverCacheMixin, PrivateMixin
from common.permissions import HasValidToken


class UserDataMixin(object):
    """
    A mixin that handles getting the UserData for a given user and access
    token.
    """

    def get_user_data_related_name(self):
        """
        Return the related_name of the UserData model in relation to the User
        model, e.g. american_gut, pgp
        """
        return self.user_data_model.user.field.related_query_name()

    def get_user_data(self):
        """
        A helper function to retrieve the given study's UserData model that
        corresponds to the request user.
        """
        # We get the UserData object this way because if we try to do it via a
        # filter the object will not be automatically created (it's an
        # AutoOneToOneField and so is only created when accessed like
        # `user.american_gut`)
        return getattr(self.request.user, self.get_user_data_related_name())

    def get_user_data_queryset(self):
        """
        A helper function to retrieve the given study's UserData model as a
        pre-filtered queryset that corresponds to the request user.
        """
        # HACK: A side effect of this call is that the UserData object will be
        # created if it doesn't exist... Which is useful for the next line,
        # which filters by it.
        self.get_user_data()

        return self.user_data_model.objects.filter(user=self.request.user)

    # TODO: Add scope permissions here?
    def get_object(self):
        """
        Get an object from its `pk`.
        """
        filters = {}

        # There's only one UserData for a given user so we don't need to filter
        # for it. We set its lookup_field to None for this reason.
        if self.lookup_field:
            filters[self.lookup_field] = self.kwargs[self.lookup_field]

        obj = get_object_or_404(self.get_queryset(), **filters)

        self.check_object_permissions(self.request, obj)

        return obj

    def perform_create(self, serializer):
        """
        perform_create is called when models are saved. We add in the user_data
        here so that on model creation it's set correctly.
        """
        serializer.save(user_data=self.get_user_data())


class UserDataDetailView(NeverCacheMixin, UserDataMixin,
                         RetrieveUpdateAPIView):
    """
    Detail view for a study's UserData object. Called with GET, PUT, or PATCH.
    """

    lookup_field = None
    permission_classes = (HasValidToken,)


class StudyDetailView(NeverCacheMixin, UserDataMixin,
                      RetrieveUpdateDestroyAPIView):
    """
    A detail view that can be GET, PUT, DELETEd.
    """

    permission_classes = (HasValidToken,)


class RetrieveStudyDetailView(NeverCacheMixin, UserDataMixin, RetrieveAPIView):
    """
    A detail view that can be GET.
    """

    permission_classes = (HasValidToken,)


class StudyListView(NeverCacheMixin, UserDataMixin, ListCreateAPIView):
    """
    A list view that can be GET or POSTed.
    """

    permission_classes = (HasValidToken,)


class StudyConnectionReturnView(PrivateMixin, TemplateView):
    """
    Handles redirecting the user to the research data page (and can be
    overridden by individual studies).
    """

    template_name = 'studies/connect-return.html'

    def __init__(self, *args, **kwargs):
        self.study_verbose_name = None
        self.badge_url = None
        self.return_url = None

        super(StudyConnectionReturnView, self).__init__(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(StudyConnectionReturnView, self).get_context_data(
            **kwargs)

        context['study_verbose_name'] = self.study_verbose_name
        context['badge_url'] = self.badge_url
        context['return_url'] = self.return_url

        return context

    def get(self, request, *args, **kwargs):
        """
        If user started on OH, go to research data. Otherwise offer choice.

        If an origin parameter exists and indicates the user started on the
        connection process on Open Humans, then send them to their research
        data page.

        Otherwise, assume the user started on the study site. Offer the option
        to return, or to continue to Open Humans.
        """
        redirect_url = reverse('my-member-connected-data')
        origin = request.GET.get('origin', '')

        # Search apps to find the study app specified by the URL 'name' slug.
        study_name = kwargs.pop('name').replace('-', '_')
        app_configs = apps.get_app_configs()

        for app_config in app_configs:
            if app_config.name.endswith(study_name):
                self.study_verbose_name = app_config.verbose_name
                self.badge_url = '{}/images/badge.png'.format(study_name)
                self.return_url = app_config.href_connect
                redirect_url = reverse(
                    'activity-management',
                    kwargs={'source': source_to_url_slug(app_config.label)})

        if origin == 'open-humans':
            return HttpResponseRedirect(redirect_url)

        if self.study_verbose_name:
            return super(StudyConnectionReturnView, self).get(
                request, *args, **kwargs)
        else:
            # TODO: Unexpected! Report error, URL should match study app.
            return HttpResponseRedirect(redirect_url)
