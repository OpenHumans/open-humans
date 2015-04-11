import re
import urlparse

from account.models import EmailAddress
from account.views import (SettingsView as AccountSettingsView,
                           SignupView as AccountSignupView)

from django.apps import apps
from django.contrib import messages as django_messages
from django.core.urlresolvers import reverse, reverse_lazy
from django.http import HttpResponseRedirect
from django.views.generic.base import RedirectView, TemplateView, View
from django.views.generic.detail import DetailView
from django.views.generic.edit import DeleteView, UpdateView
from django.views.generic.list import ListView

from oauth2_provider.models import (
    get_application_model as get_oauth2_application_model)
from oauth2_provider.views.base import (
    AuthorizationView as OriginalAuthorizationView)
from oauth2_provider.exceptions import OAuthToolkitError

from common.mixins import NeverCacheMixin, PrivateMixin
from common.utils import querydict_from_dict

from data_import.models import DataRetrievalTask


from .forms import (MyMemberChangeEmailForm,
                    MyMemberChangeNameForm,
                    MyMemberContactSettingsEditForm,
                    MyMemberProfileEditForm,
                    SignupForm)
from .models import Member


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
            'public_data':
                self.object.user.member.public_data_participant.public_files,
        })

        return context


class MemberListView(ListView):
    """
    Creates a view listing members.
    """
    context_object_name = 'members'
    paginate_by = 100
    queryset = (Member.enriched
                .exclude(user__username='api-administrator')
                .order_by('user__username'))
    template_name = 'member/member-list.html'


class MyMemberDashboardView(PrivateMixin, DetailView):
    """
    Creates a dashboard for the current user/member.

    The dashboard also displays their public member profile.
    """
    context_object_name = 'member'
    queryset = Member.enriched.all()
    template_name = 'member/my-member-dashboard.html'

    def get_object(self, queryset=None):
        return self.request.user.member

    def get_context_data(self, **kwargs):
        context = super(MyMemberDashboardView, self).get_context_data(**kwargs)

        context.update({
            'public_data':
                self.object.user.member.public_data_participant.public_files,
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

    def get_context_data(self, **kwargs):
        """
        Add a context variable for whether the email address is verified.
        """
        context = super(MyMemberSettingsEditView,
                        self).get_context_data(**kwargs)

        try:
            email = self.object.user.emailaddress_set.get(primary=True)

            context.update({'email_verified': email.verified is True})
        except EmailAddress.DoesNotExist:
            pass

        return context


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
    url = reverse_lazy('my-member-settings')

    def get_redirect_url(self, *args, **kwargs):
        redirect_field_name = self.request.REQUEST.get("redirect_field_name",
                                                       "next")
        next_url = self.request.REQUEST.get(redirect_field_name, self.url)
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
        self.datasets = (DataRetrievalTask.objects
                         .for_user(self.request.user))

        return self.datasets.normal()

    def get_context_data(self, **kwargs):
        """
        Add a context variable for whether the email address is verified.
        """
        context = super(MyMemberDatasetsView, self).get_context_data(**kwargs)

        context['failed'] = self.datasets.failed()
        context['postponed'] = self.datasets.postponed()

        return context


class DataRetrievalTaskDeleteView(PrivateMixin, DeleteView):
    """
    Let the user delete a dataset.
    """
    success_url = reverse_lazy('my-member-research-data')

    def get_queryset(self):
        return DataRetrievalTask.objects.filter(user=self.request.user)


class UserDeleteView(PrivateMixin, DeleteView):
    """
    Let the user delete their account.
    """
    context_object_name = 'user'
    template_name = 'account/delete.html'
    success_url = reverse_lazy('home')

    def get_object(self, queryset=None):
        return self.request.user


class ExceptionView(View):
    """
    Raises an exception for testing purposes.
    """
    @staticmethod
    def get(request):  # pylint: disable=unused-argument
        raise Exception('A test exception.')


class SignupView(AccountSignupView):
    """
    Creates a view for signing up for an account.

    This is a subclass of accounts' SignupView using our form customizations,
    including addition of a name field and a TOU confirmation checkbox.
    """
    form_class = SignupForm

    def create_account(self, form):
        account = super(SignupView, self).create_account(form)

        # We only create Members from this view, which means that if a User has
        # a Member then they've signed up to Open Humans and are a participant.
        member = Member(user=account.user)
        member.save()

        account.user.member.name = form.cleaned_data['name']
        account.user.member.save()

        return account

    def generate_username(self, form):
        """Override as StandardError instead of NotImplementedError."""
        raise StandardError(
            'Username must be supplied by form data.'
        )


class OAuth2LoginView(TemplateView):
    """
    Give people authorizing with us the ability to easily sign up or log in.
    """
    template_name = 'account/login-oauth2.html'

    def get_context_data(self, **kwargs):
        ctx = kwargs

        next_querystring = querydict_from_dict({
            'next': self.request.REQUEST.get('next')
        }).urlencode()

        ctx.update({
            'next_querystring': next_querystring,
            'connection': self.request.REQUEST.get('connection'),
            'panel_width': 8,
            'panel_offset': 2,
        })

        return super(OAuth2LoginView, self).get_context_data(**ctx)


class AuthorizationView(OriginalAuthorizationView):
    """
    Override oauth2_provider view to add context and customize login prompt.
    """
    def dispatch(self, request, *args, **kwargs):
        """
        Override dispatch, if unauthorized use a custom login-or-signup view.

        This renders redundant the LoginRequiredMixin used by the parent class
        (oauth_provider.views.base's AuthorizationView).
        """
        if not request.user.is_authenticated():
            try:
                # Get requesting application for custom login-or-signup
                _, credentials = self.validate_authorization_request(request)
                application_model = get_oauth2_application_model()
                application = application_model.objects.get(
                    client_id=credentials['client_id'])
            except OAuthToolkitError as error:
                return self.error_response(error)

            url = reverse('account_login_oauth2')
            url_parts = list(urlparse.urlparse(url))
            querydict = querydict_from_dict({
                'next': request.get_full_path(),
                'connection': str(application.name)
            })
            url_parts[4] = querydict.urlencode()

            return HttpResponseRedirect(urlparse.urlunparse(url_parts))

        return super(AuthorizationView, self).dispatch(
            request, *args, **kwargs)

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
        if not len(scopes) == 1:
            return False
        app_label = re.sub('-', '_', scopes[0])
        app_configs = apps.get_app_configs()
        matched_apps = [a for a in app_configs if a.label == app_label]
        if (matched_apps and len(matched_apps) == 1 and
                matched_apps[0].verbose_name == context['application'].name):
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
            context['scopes'] = [x for x in context['scopes'] if
                                 x[0] != 'read' and x[0] != 'write']
            context['is_study_app'] = True
            context['app_label'] = app_label
        return context


class ActivitiesView(NeverCacheMixin, TemplateView):
    """
    A simple TemplateView for the activities page that doesn't cache.
    """
    template_name = 'pages/activities.html'


class WelcomeView(PrivateMixin, TemplateView):
    """
    A template view that doesn't cache, and is private.
    """
    template_name = 'member/welcome.html'
