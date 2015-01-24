import os.path

from django.contrib import messages as django_messages
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseRedirect
from django.views.generic.base import View
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView
from django.views.generic.list import ListView

from account.models import EmailAddress
from account.views import (SignupView as AccountSignupView,
                           SettingsView as AccountSettingsView)

from oauth2_provider.views.base import (
    AuthorizationView as OriginalAuthorizationView)

from activities.twenty_three_and_me.models import DataFile as DataFile23andme
from common.utils import user_to_datafiles
from public_data.utils import datafiles_to_publicdatastatuses, get_public_files
from studies.views import StudyDetailView

from .forms import (MyMemberChangeEmailForm,
                    MyMemberContactSettingsEditForm,
                    MyMemberProfileEditForm,
                    SignupForm)
from .models import Member
from .serializers import MemberSerializer


class MemberDetailView(DetailView):
    """
    Creates a view of a member's public profile.
    """
    model = Member
    template_name = 'member/member-detail.html'
    slug_field = 'user__username'

    def get_context_data(self, **kwargs):
        """Add context so login and signup return to this page."""
        context = super(MemberDetailView, self).get_context_data(**kwargs)
        context.update({
            'redirect_field_name': 'next',
            'redirect_field_value': reverse_lazy(
                'member-detail',
                kwargs={'slug': self.object.user.username}),
            'public_data': get_public_files(self.object.user),
        })
        return context


class MemberListView(ListView):
    """
    Creates a view listing members.
    """
    model = Member
    template_name = 'member/member-list.html'


class MyMemberDashboardView(DetailView):
    """
    Creates a dashboard for the current user/member.

    The dashboard also displays their public member profile.
    """
    context_object_name = 'member'
    model = Member
    template_name = 'member/my-member-dashboard.html'

    def get_object(self, queryset=None):
        return self.request.user.member


class MyMemberProfileEditView(UpdateView):
    """
    Creates an edit view of the current user's public member profile.
    """
    form_class = MyMemberProfileEditForm
    model = Member
    template_name = 'member/my-member-profile-edit.html'
    success_url = reverse_lazy('my-member-dashboard')

    def get_object(self, queryset=None):
        return self.request.user.member


class MyMemberSettingsEditView(UpdateView):
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


class MyMemberChangeEmailView(AccountSettingsView):
    """
    Creates a view for the current user to change their email.

    This is an email-only subclass of account's SettingsView.
    """
    form_class = MyMemberChangeEmailForm
    template_name = 'member/my-member-change-email.html'
    success_url = reverse_lazy('my-member-settings')
    messages = {
        "settings_updated": {
            "level": django_messages.SUCCESS,
            "text": "Email address updated and confirmation email sent."
        },
    }

    def get_success_url(self, *args, **kwargs):
        kwargs.update(
            {'fallback_url': reverse_lazy('my-member-settings')})
        return super(MyMemberChangeEmailView, self).get_success_url(
            *args, **kwargs)


class MyMemberSendConfirmationEmailView(View):
    def get(self, request):
        email_address = request.user.emailaddress_set.get(primary=True)
        email_address.send_confirmation()

        django_messages.success(request,
                                ('A confirmation email was sent to "{}".'
                                 .format(email_address.email)))

        return HttpResponseRedirect(reverse_lazy('my-member-settings'))


class MyMemberDatasetsView(ListView):
    """
    Creates a view for displaying and importing research/activity datasets.
    """
    template_name = "member/my-member-research-data.html"
    context_object_name = 'data_sets'

    def get_queryset(self):
        data_files = user_to_datafiles(self.request.user)
        try:
            if self.request.user.member.public_data_participant.enrolled:
                public_statuses = datafiles_to_publicdatastatuses(data_files)
                for i in range(len(data_files)):
                    if public_statuses[i].is_public:
                        data_files[i].is_public = True
        except ObjectDoesNotExist:
            pass
        return data_files


class ExceptionView(View):
    """
    Raises an exception for testing purposes.
    """
    def get(self, request):
        raise Exception('A test exception.')


class SignupView(AccountSignupView):
    """
    Creates a view for signing up for an account.

    This is a subclass of accounts' SignupView using our form customizations,
    including addition of a TOU confirmation checkbox.
    """
    form_class = SignupForm

    def generate_username(self, form):
        """Override as StandardError instead of NotImplementedError."""
        raise StandardError(
            "Username must be supplied by form data."
        )


class AuthorizationView(OriginalAuthorizationView):
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

        return context


# TODO: This should go in open_humans/api_views.py
class MemberDetail(StudyDetailView):
    def get_queryset(self):
        return User.objects.filter(pk=self.request.user.pk)

    serializer_class = MemberSerializer
