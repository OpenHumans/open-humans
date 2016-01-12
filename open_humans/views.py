import re
import urlparse

from operator import attrgetter

from account.views import (LoginView as AccountLoginView,
                           SettingsView as AccountSettingsView,
                           SignupView as AccountSignupView)

from django.apps import apps
from django.conf import settings
from django.contrib import messages as django_messages
from django.contrib.auth import logout
from django.core.urlresolvers import reverse, reverse_lazy
from django.db.models import Count
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import redirect
from django.views.generic.base import RedirectView, TemplateView, View
from django.views.generic.detail import DetailView
from django.views.generic.edit import DeleteView, FormView, UpdateView
from django.views.generic.list import ListView

from oauth2_provider.models import (
    get_application_model as get_oauth2_application_model,
    AccessToken)
from oauth2_provider.views.base import (
    AuthorizationView as OriginalAuthorizationView)
from oauth2_provider.exceptions import OAuthToolkitError

from common.mixins import NeverCacheMixin, PrivateMixin
from common.utils import app_from_label, querydict_from_dict

from activities.runkeeper.models import UserData as UserDataRunKeeper
from data_import.models import DataRetrievalTask
from data_import.utils import app_name_to_data_file_model, get_source_names
from public_data.models import PublicDataAccess
from studies.models import StudyGrant
from studies.american_gut.models import UserData as UserDataAmericanGut
from studies.go_viral.models import UserData as UserDataGoViral
from studies.pgp.models import UserData as UserDataPgp
from studies.wildlife.models import UserData as UserDataWildLife

from .forms import (EmailUserForm,
                    MemberLoginForm,
                    MemberSignupForm,
                    MyMemberChangeEmailForm,
                    MyMemberChangeNameForm,
                    MyMemberContactSettingsEditForm,
                    MyMemberProfileEditForm)
from .models import Member, EmailMetadata


class MemberDetailView(DetailView):
    """
    Creates a view of a member's public profile.
    """
    queryset = Member.enriched.all()
    template_name = 'member/member-detail.html'
    slug_field = 'user__username'

    def get_context_data(self, **kwargs):
        """
        Add context so login and signup return to this page.

        TODO: Document why returning to the page is desired (I think because
        you need to be signed in to contact a member?)
        """
        context = super(MemberDetailView, self).get_context_data(**kwargs)

        context.update({
            'next': reverse_lazy('member-detail',
                                 kwargs={'slug': self.object.user.username}),
            'public_data_tasks':
                self.object.public_data_participant.public_data_tasks,
        })

        return context


class MemberListView(ListView):
    """
    Creates a view listing members.
    """
    context_object_name = 'members'
    paginate_by = 50
    template_name = 'member/member-list.html'

    def get_queryset(self):
        if self.request.GET.get('sort') == 'username':
            return (Member.enriched
                    .exclude(user__username='api-administrator')
                    .order_by('user__username'))

        # First sort by name and username
        sorted_members = sorted(Member.enriched
                                .exclude(user__username='api-administrator'),
                                key=attrgetter('user.username'))

        # Then sort by number of badges
        sorted_members = sorted(sorted_members,
                                key=lambda m: len(m.badges),
                                reverse=True)

        return sorted_members

    def get_context_data(self, **kwargs):
        """
        Add context for sorting button.
        """
        context = super(MemberListView, self).get_context_data(**kwargs)

        if self.request.GET.get('sort') == 'username':
            sort_direction = 'connections'
            sort_description = 'by number of connections'
        else:
            sort_direction = 'username'
            sort_description = 'by username'

        context.update({
            'sort_direction': sort_direction,
            'sort_description': sort_description,
        })

        return context


class MyMemberDashboardView(PrivateMixin, DetailView):
    """
    Creates a dashboard for the current user/member.

    The dashboard also displays their public member profile.
    """
    context_object_name = 'member'
    queryset = Member.enriched.all()
    template_name = 'member/my-member-dashboard.html'

    def get_object(self, queryset=None):
        return Member.enriched.get(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super(MyMemberDashboardView, self).get_context_data(**kwargs)
        context.update({
            'public_data_tasks': (self.object.user.member
                                  .public_data_participant
                                  .public_data_tasks),
        })

        return context


class MyMemberProfileEditView(PrivateMixin, UpdateView):
    """
    Creates an edit view of the current user's public member profile.
    """
    form_class = MyMemberProfileEditForm
    model = Member
    template_name = 'member/my-member-profile-edit.html'
    success_url = reverse_lazy('my-member-dashboard')

    def get_object(self, queryset=None):
        return self.request.user.member


class MyMemberSettingsEditView(PrivateMixin, UpdateView):
    """
    Creates an edit view of the current user's member account settings.
    """
    form_class = MyMemberContactSettingsEditForm
    model = Member
    template_name = 'member/my-member-settings.html'
    success_url = reverse_lazy('my-member-settings')

    def get_object(self, queryset=None):
        return self.request.user.member


class MyMemberChangeEmailView(PrivateMixin, AccountSettingsView):
    """
    Creates a view for the current user to change their email.

    This is an email-only subclass of account's SettingsView.
    """
    form_class = MyMemberChangeEmailForm
    template_name = 'member/my-member-change-email.html'
    success_url = reverse_lazy('my-member-settings')
    messages = {
        'settings_updated': {
            'level': django_messages.SUCCESS,
            'text': 'Email address updated and confirmation email sent.'
        },
    }

    def get_success_url(self, *args, **kwargs):
        kwargs.update(
            {'fallback_url': reverse_lazy('my-member-settings')})
        return super(MyMemberChangeEmailView, self).get_success_url(
            *args, **kwargs)


class MyMemberChangeNameView(PrivateMixin, UpdateView):
    """
    Creates an edit view of the current member's name.
    """
    form_class = MyMemberChangeNameForm
    model = Member
    template_name = 'member/my-member-change-name.html'
    success_url = reverse_lazy('my-member-settings')

    def get_object(self, queryset=None):
        return self.request.user.member


class MyMemberSendConfirmationEmailView(PrivateMixin, RedirectView):
    """
    Send a confirmation email and redirect back to the settings page.
    """
    permanent = False
    url = reverse_lazy('my-member-settings')

    def get_redirect_url(self, *args, **kwargs):
        redirect_field_name = self.request.GET.get('redirect_field_name',
                                                   'next')
        next_url = self.request.GET.get(redirect_field_name, self.url)
        return next_url

    def dispatch(self, request, *args, **kwargs):
        email_address = request.user.emailaddress_set.get(primary=True)
        email_address.send_confirmation()
        django_messages.success(request,
                                ('A confirmation email was sent to "{}".'
                                 .format(email_address.email)))
        return super(MyMemberSendConfirmationEmailView, self).dispatch(
            request, *args, **kwargs)


class MyMemberDatasetsView(PrivateMixin, ListView):
    """
    Creates a view for displaying and importing research/activity datasets.
    """
    template_name = 'member/my-member-research-data.html'
    context_object_name = 'data_retrieval_tasks'

    def get_queryset(self):
        # pylint: disable=attribute-defined-outside-init
        datasets = (DataRetrievalTask.objects
                    .for_user(self.request.user)
                    .grouped_recent())

        return datasets

    def get_context_data(self, **kwargs):
        """
        Add DataRetrievalTask to the request context.
        """
        context = super(MyMemberDatasetsView, self).get_context_data(**kwargs)

        context['DataRetrievalTask'] = DataRetrievalTask

        return context


class MyMemberConnectionsView(PrivateMixin, TemplateView):
    """
    A view for a member to manage their connections.
    """

    template_name = 'member/my-member-connections.html'

    def get_context_data(self, **kwargs):
        """
        Add connections and study_grants to the request context.
        """
        context = super(MyMemberConnectionsView, self).get_context_data(
            **kwargs)

        context.update({
            'connections': self.request.user.member.connections.items(),
            'study_grants': self.request.user.member.study_grants.all(),
        })

        return context


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

        data_file_model = app_name_to_data_file_model(source)

        return data_file_model.objects.filter(
            user_data__user=self.request.user)

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


class UserDeleteView(PrivateMixin, DeleteView):
    """
    Let the user delete their account.
    """
    context_object_name = 'user'
    template_name = 'account/delete.html'
    success_url = reverse_lazy('home')

    def delete(self, request, *args, **kwargs):
        response = super(UserDeleteView, self).delete(request, *args, **kwargs)

        # Log the user out prior to deleting them so that they don't appear
        # logged in when they're redirected to the homepage.
        logout(request)

        return response

    def get_object(self, queryset=None):
        return self.request.user


class MyMemberConnectionDeleteView(PrivateMixin, TemplateView):
    """
    Let the user delete a connection.
    """

    template_name = 'member/my-member-connections-delete.html'

    def get_access_tokens(self, connection):
        connections = self.request.user.member.connections

        if connection not in connections:
            raise Http404()

        access_tokens = AccessToken.objects.filter(
            user=self.request.user,
            application__name=connections[connection]['verbose_name'],
            application__user__username='api-administrator')

        return access_tokens

    def get_context_data(self, **kwargs):
        context = super(MyMemberConnectionDeleteView, self).get_context_data(
            **kwargs)

        connection = kwargs.get('connection', None)
        connections = self.request.user.member.connections

        if connection and connection in connections:
            context.update({
                'connection_name': connections[connection]['verbose_name'],
            })

        return context

    def post(self, request, **kwargs):
        connection = kwargs.get('connection', None)
        connections = self.request.user.member.connections

        if not connection or connection not in connections:
            return HttpResponseRedirect(reverse('my-member-connections'))

        if request.POST.get('remove_datafiles', 'off') == 'on':
            data_file_model = app_name_to_data_file_model(connection)

            data_file_model.objects.filter(
                user_data__user=self.request.user).delete()

        # TODO: Automatic list of all current studies.
        if connection in ('american_gut', 'go_viral', 'pgp', 'wildlife'):
            access_tokens = self.get_access_tokens(connection)
            access_tokens.delete()

            return HttpResponseRedirect(reverse('my-member-connections'))

        if connection == 'runkeeper':
            django_messages.error(
                request,
                ('Sorry, RunKeeper connections must currently be removed by '
                 'visiting http://runkeeper.com/settings/apps'))

            return HttpResponseRedirect(reverse('my-member-connections'))

        if connection == 'twenty_three_and_me':
            user_data = request.user.twenty_three_and_me
            user_data.genome_file.delete(save=True)
            django_messages.warning(
                request,
                ('We have deleted your original uploaded 23andMe file. You '
                 'will need to remove your processed files separately on your '
                 'research data management page.'))
            return HttpResponseRedirect(reverse('my-member-connections'))


class MyMemberStudyGrantDeleteView(PrivateMixin, TemplateView):
    """
    Let the user delete a study grant.
    """

    template_name = 'member/my-member-study-grants-delete.html'

    @staticmethod
    def get_study_grant(request, **kwargs):
        try:
            study_grant_pk = kwargs.get('study_grant')
            study_grant = StudyGrant.objects.get(pk=study_grant_pk,
                                                 member=request.user.member)
        except StudyGrant.DoesNotExist:
            return None

        return study_grant

    def get_context_data(self, **kwargs):
        context = super(MyMemberStudyGrantDeleteView, self).get_context_data(
            **kwargs)

        study_grant = self.get_study_grant(self.request, **kwargs)

        if study_grant:
            context.update({
                'study_title': study_grant.study.title,
            })

        return context

    def post(self, request, **kwargs):
        study_grant = self.get_study_grant(request, **kwargs)

        if not study_grant:
            return

        study_grant.delete()

        return HttpResponseRedirect(reverse('my-member-connections'))


class ExceptionView(View):
    """
    Raises an exception for testing purposes.
    """
    @staticmethod
    def get(request):  # pylint: disable=unused-argument
        raise Exception('A test exception.')


class MemberSignupView(AccountSignupView):
    """
    Creates a view for signing up for a Member account.

    This is a subclass of accounts' SignupView using our form customizations,
    including addition of a name field and a TOU confirmation checkbox.
    """
    form_class = MemberSignupForm

    def create_account(self, form):
        account = super(MemberSignupView, self).create_account(form)

        # We only create Members from this view, which means that if a User has
        # a Member then they've signed up to Open Humans and are a participant.
        member = Member(user=account.user)

        newsletter = form.data.get('newsletter', 'off') == 'on'
        allow_user_messages = (form.data.get('allow_user_messages', 'off') ==
                               'on')

        member.newsletter = newsletter
        member.allow_user_messages = allow_user_messages

        member.save()

        account.user.member.name = form.cleaned_data['name']
        account.user.member.save()

        return account

    def generate_username(self, form):
        """Override as StandardError instead of NotImplementedError."""
        raise StandardError(
            'Username must be supplied by form data.'
        )


class MemberLoginView(AccountLoginView):
    """
    A version of account's LoginView that requires the User to be a Researcher.
    """
    form_class = MemberLoginForm


class OAuth2LoginView(TemplateView):
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
            'panel_width': 8,
            'panel_offset': 2,
        })

        return super(OAuth2LoginView, self).get_context_data(**kwargs)


def origin(string):
    """
    Coerce an origin to 'open-humans' or 'external', defaulting to 'external'
    """
    return 'open-humans' if string == 'open-humans' else 'external'


class AuthorizationView(OriginalAuthorizationView):
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
        app = app_from_label(app_label)

        if app and app.verbose_name == context['application'].name:
            return app_label

        return False

    def get_context_data(self, **kwargs):
        context = super(AuthorizationView, self).get_context_data(**kwargs)

        context.update({
            'panel_width': 8,
            'panel_offset': 2
        })

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

            context['app'] = app_from_label(app_label)
            context['app_label'] = app_label
            context['is_study_app'] = True
            context['scopes'] = [x for x in context['scopes']
                                 if x[0] != 'read' and x[0] != 'write']

        return context

    def get_template_names(self):
        if self.is_study_app:
            return ['oauth2_provider/finalize.html']

        return [self.template_name]


class SourcesContextMixin(object):
    """
    A mixin for adding context for connection sources to a template.
    """

    def get_context_data(self, **kwargs):
        context = super(SourcesContextMixin, self).get_context_data(**kwargs)

        context.update({
            'sources': {
                'american_gut': UserDataAmericanGut,
                'go_viral': UserDataGoViral,
                'pgp': UserDataPgp,
                'runkeeper': UserDataRunKeeper,
                'wildlife': UserDataWildLife,
            }
        })

        return context


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
        for source_name in get_source_names():
            app_config = apps.get_app_config(source_name)
            source_connections[source_name] = [
                {'user': ud.user, 'public_data_access':
                 PublicDataAccess.objects.filter(
                     participant=ud.user.member.public_data_participant,
                     data_source=source_name)}
                for ud in app_config.get_model('UserData').objects.all() if
                ud.is_connected]
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
    template_name = 'member/welcome.html'


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
        else:
            return super(HomeView, self).get(request, *args, **kwargs)


class EmailUserView(PrivateMixin, DetailView, FormView):
    """
    A simple form view for allowing a user to email another user.
    """
    form_class = EmailUserForm
    queryset = Member.enriched.all()
    slug_field = 'user__username'
    template_name = 'member/member-email.html'

    def get_success_url(self):
        return reverse('member-detail',
                       kwargs={'slug': self.get_object().user.username})

    def form_valid(self, form):
        sender = self.request.user
        receiver = self.get_object().user

        if not receiver.member.allow_user_messages:
            django_messages.error(self.request,
                                  ('Sorry, {} does not accept user messages.'
                                   .format(receiver.username)))

            return HttpResponseRedirect(self.get_success_url())

        form.send_mail(sender, receiver)

        metadata = EmailMetadata(sender=sender, receiver=receiver)
        metadata.save()

        django_messages.success(self.request,
                                ('Your message was sent to {}.'
                                 .format(receiver.username)))

        return super(EmailUserView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(EmailUserView, self).get_context_data(**kwargs)

        context.update({
            'panel_width': 8,
            'panel_offset': 2,
        })

        return context
