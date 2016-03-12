import re
import urlparse

from django.apps import apps
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse, reverse_lazy
from django.db.models import Count
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.views.generic.base import TemplateView, View
from django.views.generic.edit import DeleteView

from oauth2_provider.models import (
    get_application_model as get_oauth2_application_model)
from oauth2_provider.views.base import (
    AuthorizationView as OriginalAuthorizationView)
from oauth2_provider.exceptions import OAuthToolkitError

from common.mixins import LargePanelMixin, NeverCacheMixin, PrivateMixin
from common.utils import (querydict_from_dict, get_source_labels,
                          get_source_labels_and_configs)


from data_import.models import DataFile
from public_data.models import PublicDataAccess

from .mixins import SourcesContextMixin
from .models import Member

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


def origin(string):
    """
    Coerce an origin to 'open-humans' or 'external', defaulting to 'external'
    """
    return 'open-humans' if string == 'open-humans' else 'external'


class AuthorizationView(LargePanelMixin, OriginalAuthorizationView):
    """
    Override oauth2_provider view to add origin, context, and customize login
    prompt.
    """

    is_study_app = False

    def create_authorization_response(self, request, scopes, credentials,
                                      allow):
        """
        Add the origin to the callback URL.
        """
        uri, headers, body, status = (
            super(AuthorizationView, self).create_authorization_response(
                request, scopes, credentials, allow))

        uri += '&origin={}'.format(origin(request.GET.get('origin')))

        return (uri, headers, body, status)

    def dispatch(self, request, *args, **kwargs):
        """
        Override dispatch, if unauthorized use a custom login-or-signup view.

        This renders redundant the LoginRequiredMixin used by the parent class
        (oauth_provider.views.base's AuthorizationView).
        """
        if request.user.is_authenticated():
            return (super(AuthorizationView, self)
                    .dispatch(request, *args, **kwargs))

        try:
            # Get requesting application for custom login-or-signup
            _, credentials = self.validate_authorization_request(request)

            application_model = get_oauth2_application_model()

            application = application_model.objects.get(
                client_id=credentials['client_id'])
        except OAuthToolkitError as error:
            return self.error_response(error)

        querydict = querydict_from_dict({
            'next': request.get_full_path(),
            'connection': str(application.name)
        })

        url = reverse('account_login_oauth2')

        url_parts = list(urlparse.urlparse(url))
        url_parts[4] = querydict.urlencode()

        return HttpResponseRedirect(urlparse.urlunparse(url_parts))

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


class ActivitiesView(NeverCacheMixin, SourcesContextMixin, TemplateView):
    """
    A simple TemplateView for the activities page that doesn't cache.
    """

    template_name = 'pages/activities.html'


class StatisticsView(TemplateView):
    """
    A simple TemplateView for Open Humans statistics.

    @madprime 2015/12/10: Updates on how file sharing was managed per-source
    broke this. This fixed version is very slow & doesn't restore all features.
    """
    template_name = 'pages/statistics.html'

    @staticmethod
    def get_inbound_connections():
        """
        Inbound connections is currently shorthand for study connections.

        Inbound connections can be data-push integrations like PGP or hosted
        studies like Keeping Pace; "inbound" means that we host the OAuth2
        provider.
        """
        application_model = get_oauth2_application_model()

        return (application_model.objects
                .order_by('name')
                .annotate(count=Count('accesstoken__user', distinct=True)))

    def get_source_connections(self):
        source_connections = {}
        private_source_connections = {}
        public_source_connections = {}

        for source_name in get_source_labels():
            source_connections[source_name] = [
                {
                    'user': user,
                    'public_data_access': PublicDataAccess.objects.filter(
                        participant=user.member.public_data_participant,
                        data_source=source_name)
                }
                for user in User.objects.filter(member__isnull=False)
                if getattr(user, source_name).is_connected]

            private_source_connections[source_name] = [
                x for x in source_connections[source_name] if
                not x['public_data_access'] or
                not x['public_data_access'][0].is_public]

            public_source_connections[source_name] = [
                x for x in source_connections[source_name] if
                x['public_data_access'] and
                x['public_data_access'][0].is_public]

        self.source_connections = source_connections
        self.private_source_connections = private_source_connections
        self.public_source_connections = public_source_connections

    @staticmethod
    def get_two_plus_users(is_public):
        """Currently broken."""
        return None

    def get_two_plus_public(self):
        """Currently broken."""
        return None

    def get_two_plus_private(self):
        """Currently broken."""
        return None

    def get_context_data(self, **kwargs):
        context = super(StatisticsView, self).get_context_data(**kwargs)
        self.get_source_connections()

        context.update({
            'members': Member.objects.count(),
            'studies': self.get_inbound_connections(),
            'data_sources': self.source_connections,
            'private_sources': self.private_source_connections,
            'public_sources': self.public_source_connections,
            'public_two_plus': self.get_two_plus_public,
            'private_two_plus': self.get_two_plus_private,
        })

        return context


class WelcomeView(PrivateMixin, SourcesContextMixin, TemplateView):
    """
    A template view that doesn't cache, and is private.
    """
    template_name = 'welcome/index.html'


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


class HomeView(TemplateView):
    """
    Redirect to the welcome page if the user is logged in.
    """
    template_name = 'pages/home.html'

    def get(self, request, *args, **kwargs):
        if not request.user.is_anonymous():
            return redirect(settings.LOGIN_REDIRECT_URL)

        return super(HomeView, self).get(request, *args, **kwargs)


class ResearchPageView(TemplateView):
    """
    Add current sources to template context.
    """

    template_name = 'pages/research.html'

    def split_n(self, x, n):
        """
        Split list x into n lists of near-equal size.
        """
        remainder = len(x) % n
        splits = []
        index_start, index_end = 0, 0
        for i in range(n):
            if i < remainder:
                index_end += 1 + len(x) / n
            else:
                index_end += len(x) / n
            splits.append(x[index_start:index_end])
            index_start = index_end
        return splits

    def get_context_data(self, **kwargs):
        """Add sources, split 2/3/4-way for rendering in divs."""
        context = super(ResearchPageView, self).get_context_data(**kwargs)
        sources = get_source_labels_and_configs()
        context.update({
            'sources_2split': self.split_n(sources, 2),
            'sources_3split': self.split_n(sources, 3),
            'sources_4split': self.split_n(sources, 4),
        })

        return context
