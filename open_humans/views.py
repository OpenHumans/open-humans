from account.views import SignupView as AccountSignupView

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse_lazy
from django.views.generic.base import View
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView
from django.views.generic.list import ListView

from activities.twenty_three_and_me.models import ActivityDataFile as \
    ActivityDataFile23andme

from .forms import ProfileEditForm, SettingsEditForm, SignupForm
from .models import Profile
from .serializers import ProfileSerializer
from .viewsets import SimpleCurrentUserViewset


class MemberProfileDetailView(DetailView):
    """View of a member's public profile."""
    model = Profile
    template_name = 'profile/member_detail.html'
    slug_field = 'user__username'


class MemberProfileListView(ListView):
    """View of a member's public profile."""
    model = Profile
    template_name = 'profile/member_list.html'


class UserProfileDashboardView(DetailView):
    """Dashboard, contains view of the current user's profile."""
    context_object_name = 'profile'
    model = Profile
    template_name = 'profile/dashboard.html'

    def get_object(self, queryset=None):
        return self.request.user.profile


class UserProfileEditView(UpdateView):
    """An edit view of the current user's profile."""
    form_class = ProfileEditForm
    model = Profile
    template_name = 'profile/edit.html'
    success_url = reverse_lazy('profile_dashboard')

    def get_object(self, queryset=None):
        return self.request.user.profile


class UserSettingsEditView(UpdateView):
    """
    An edit view of the current user's profile.
    """
    form_class = SettingsEditForm
    model = Profile
    template_name = 'profile/account_settings.html'
    success_url = reverse_lazy('profile_account_settings')

    def get_object(self, queryset=None):
        return self.request.user.profile


# TODO: Make more generic.
class DatasetsView(ListView):
    """
    View data imported by Open Humans member.
    """
    model = ActivityDataFile23andme
    template_name = "profile/research_data.html"
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


class ProfileViewSet(SimpleCurrentUserViewset):
    queryset = User.objects.all()
    serializer_class = ProfileSerializer
