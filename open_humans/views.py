import re

from collections import OrderedDict

from django.apps import apps
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import render
from django.views.generic.base import TemplateView, View
from django.views.generic.edit import DeleteView

from common.activities import (personalize_activities,
                               personalize_activities_dict)
from common.mixins import LargePanelMixin, NeverCacheMixin, PrivateMixin
from common.utils import querydict_from_dict
from common.views import BaseOAuth2AuthorizationView

from data_import.models import DataFile
from private_sharing.models import DataRequestProject

from .mixins import SourcesContextMixin

User = get_user_model()


class SourceDataFilesDeleteView(PrivateMixin, DeleteView):
    """
    Let the user delete all datafiles for a source. Note that DeleteView was
    written with a single object in mind but will happily delete a QuerySet due
    to duck-typing.
    """
    template_name = 'member/my-member-source-data-files-delete.html'
    success_url = reverse_lazy('my-member-research-data')

    def get_object(self, queryset=None):
        source = self.kwargs['source']

        return DataFile.objects.filter(user=self.request.user, source=source)

    def get_context_data(self, **kwargs):
        """
        Add the source to the request context.
        """
        context = super(SourceDataFilesDeleteView, self).get_context_data(
            **kwargs)

        context.update({
            'source': self.kwargs['source'],
        })

        return context


class ExceptionView(View):
    """
    Raises an exception for testing purposes.
    """
    @staticmethod
    def get(request):  # pylint: disable=unused-argument
        raise Exception('A test exception.')


class OAuth2LoginView(LargePanelMixin, TemplateView):
    """
    Give people authorizing with us the ability to easily sign up or log in.
    """
    template_name = 'account/login-oauth2.html'

    def get_context_data(self, **kwargs):
        next_querystring = querydict_from_dict({
            'next': self.request.GET.get('next')
        }).urlencode()

        kwargs.update({
            'next_querystring': next_querystring,
            'connection': self.request.GET.get('connection'),
        })

        return super(OAuth2LoginView, self).get_context_data(**kwargs)


class AuthorizationView(BaseOAuth2AuthorizationView):
    """
    Add checks for study apps to the OAuth2 authorization view.
    """

    is_study_app = False

    @staticmethod
    def _check_study_app_request(context):
        """
        Return true if this OAuth2 request matches a study app
        """
        # NOTE: This assumes 'scopes' was overwritten by get_context_data.
        scopes = [x[0] for x in context['scopes']]

        try:
            scopes.remove('read')
            scopes.remove('write')
        except ValueError:
            return False

        if len(scopes) != 1:
            return False

        app_label = re.sub('-', '_', scopes[0])
        app = apps.get_app_config(app_label)

        if app and app.verbose_name == context['application'].name:
            return app_label

        return False

    def get_context_data(self, **kwargs):
        context = super(AuthorizationView, self).get_context_data(**kwargs)

        def scope_key(zipped_scope):
            scope, _ = zipped_scope

            # Sort 'write' second to last
            if scope == 'write':
                return 'zzy'

            # Sort 'read' last
            if scope == 'read':
                return 'zzz'

            # Sort all other scopes alphabetically
            return scope

        def scope_class(scope):
            if scope in ['read', 'write']:
                return 'info'

            return 'primary'

        zipped_scopes = zip(context['scopes'], context['scopes_descriptions'])
        zipped_scopes.sort(key=scope_key)

        context['scopes'] = [(scope, description, scope_class(scope))
                             for scope, description in zipped_scopes]

        # For custom display when it's for a study app connection.
        app_label = self._check_study_app_request(context)

        if app_label:
            self.is_study_app = True

            context['app'] = apps.get_app_config(app_label)
            context['app_label'] = app_label
            context['is_study_app'] = True
            context['scopes'] = [x for x in context['scopes']
                                 if x[0] != 'read' and x[0] != 'write']

        return context

    def get_template_names(self):
        if self.is_study_app:
            return ['oauth2_provider/finalize.html']

        return [self.template_name]


class HomeView(NeverCacheMixin, SourcesContextMixin, TemplateView):
    """
    List activities on homepage, don't cache.
    """

    template_name = 'pages/home.html'

    def get_context_data(self, *args, **kwargs):
        context = super(HomeView,
                        self).get_context_data(*args, **kwargs)

        context.update({
            'activities': personalize_activities(self.request.user)
        })

        return context


class PGPInterstitialView(PrivateMixin, TemplateView):
    """
    An interstitial view shown to PGP members with 1 or more private PGP
    datasets and no public PGP datasets.
    """
    template_name = 'pages/pgp-interstitial.html'

    def get(self, request, *args, **kwargs):
        request.user.member.seen_pgp_interstitial = True
        request.user.member.save()

        return super(PGPInterstitialView, self).get(request, *args, **kwargs)


class ResearchPageView(TemplateView):
    """
    Add current sources to template context.
    """

    template_name = 'pages/research.html'

    def get_context_data(self, **kwargs):
        """
        Update context with same source data used by the activities grid.
        """
        context = super(ResearchPageView, self).get_context_data(**kwargs)
        activities = sorted(personalize_activities(self.request.user),
                            key=lambda k: k['source_name'].lower())
        sources = OrderedDict([
            (activity['source_name'], activity) for activity in activities if
            'data_source' in activity and activity['data_source']
        ])
        context.update({'sources': sources})
        return context


class ActivityManagementView(LargePanelMixin, TemplateView):

    source = None
    template_name = 'member/activity-management.html'

    @property
    def activity(self):
        def get_url_identifier(activity):
            return (activity.get('url_slug') or
                    activity.get('source_name'))

        activities = {get_url_identifier(activity): activity
                      for activity
                      in personalize_activities(self.request.user)}

        return activities[self.kwargs['source']]

    def requesting_activities(self):
        activities = []

        for project in DataRequestProject.objects.filter(approved=True,
                                                         active=True):
            if self.activity['source_name'] in project.request_sources_access:
                activities.append({
                    'name': project.name,
                    'slug': project.slug,
                    'joined': project.is_joined(self.request.user),
                })

        return activities

    def get_context_data(self, **kwargs):
        context = super(ActivityManagementView, self).get_context_data(
            **kwargs)

        context.update({
            'activity': self.activity,
            'activities': personalize_activities_dict(self.request.user),
            'source': self.activity['source_name'],
            'public_files': (DataFile.objects
                             .filter(source=self.activity['source_name'])
                             .current()).count(),
            'requesting_activities': self.requesting_activities(),
        })

        if 'project_id' in self.activity:
            context.update({
                'project': (DataRequestProject.objects
                            .get(pk=self.activity['project_id']))
            })

        if self.request.user.is_authenticated():
            context.update({
                'data_files': (DataFile.objects
                               .for_user(self.request.user)
                               .filter(source=self.kwargs['source'])),
            })

        return context


def server_error(request):
    response = render(request, '500.html')
    response.status_code = 500

    return response
