from account.views import (SignupView as AccountSignupView,
                           SettingsView as AccountSettingsView)

from django.contrib import messages
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse_lazy
from django.views.generic.base import View
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView
from django.views.generic.list import ListView

from activities.twenty_three_and_me.models import ActivityDataFile as \
    ActivityDataFile23andme

from .forms import (MyMemberChangeEmailForm,
                    MyMemberContactSettingsEditForm,
                    MyMemberProfileEditForm,
                    SignupForm)
from .models import Member
from .serializers import ProfileSerializer
from .viewsets import SimpleCurrentUserViewset


class MemberDetailView(DetailView):
    """View of a member's public profile."""
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
        })
        return context


class MemberListView(ListView):
    """View of a member's public profile."""
    model = Member
    template_name = 'member/member-list.html'


class MyMemberDashboardView(DetailView):
    """Dashboard, contains view of the current user's profile."""
    context_object_name = 'member'
    model = Member
    template_name = 'member/my-member-dashboard.html'

    def get_object(self, queryset=None):
        return self.request.user.member


class MyMemberProfileEditView(UpdateView):
    """An edit view of the current member's profile."""
    form_class = MyMemberProfileEditForm
    model = Member
    template_name = 'member/my-member-profile-edit.html'
    success_url = reverse_lazy('my-member-dashboard')

    def get_object(self, queryset=None):
        return self.request.user.member


class MyMemberSettingsEditView(UpdateView):
    """An edit view of the current user's member account settings."""
    form_class = MyMemberContactSettingsEditForm
    model = Member
    template_name = 'member/my-member-settings.html'
    success_url = reverse_lazy('my-member-settings')

    def get_object(self, queryset=None):
        return self.request.user.member


class MyMemberChangeEmailView(AccountSettingsView):
    """Email-only subclass of account's SettingsView."""
    form_class = MyMemberChangeEmailForm
    template_name = 'member/my-member-change-email.html'
    success_url = reverse_lazy('my-member-settings')
    messages = {
        "settings_updated":
        {"level": messages.SUCCESS,
         "text": "Email address updated and confirmation email sent."
         },
        }

    def get_success_url(self, *args, **kwargs):
        kwargs.update(
            {'fallback_url': reverse_lazy('my-member-settings')})
        return super(MyMemberChangeEmailView, self).get_success_url(
            *args, **kwargs)


# TODO: Make more generic.
class MyMemberDatasetsView(ListView):
    """View data imported by Open Humans member."""
    model = ActivityDataFile23andme
    template_name = "member/my-member-research-data.html"
    context_object_name = 'data_sets'

    def get_queryset(self):
        return ActivityDataFile23andme.objects.filter(
            study_user__user=self.request.user)


class ExceptionView(View):
    """
    Raises an exception for testing purposes.
    """
    def get(self, request):
        raise Exception('A test exception.')


class SignupView(AccountSignupView):
    """A subclass of SignupView that uses our form customizations."""
    form_class = SignupForm

    def generate_username(self, form):
        """Override as StandardError instead of NotImplementedError."""
        raise StandardError(
            "Username must be supplied by form data."
        )

# TODO: change to MemberViewSet? And filter to Users that are also Members.
class ProfileViewSet(SimpleCurrentUserViewset):
    queryset = User.objects.all()
    serializer_class = ProfileSerializer
