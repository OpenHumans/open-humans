from account.views import SignupView

from django.core.urlresolvers import reverse_lazy
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView
from django.views.generic.list import ListView

from .forms import CustomSignupForm, ProfileEditForm
from .models import Profile


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
    """
    Dashboard, contains view of the current user's profile.
    """
    context_object_name = 'profile'
    model = Profile
    template_name = 'profile/dashboard.html'

    def get_object(self, queryset=None):
        return self.request.user.profile


class UserProfileEditView(UpdateView):
    """
    An edit view of the current user's profile.
    """
    form_class = ProfileEditForm
    model = Profile
    template_name = 'profile/edit.html'
    success_url = reverse_lazy('profile_dashboard')

    def get_object(self, queryset=None):
        return self.request.user.profile


class UserProfileSignupSetup(UpdateView):
    """
    An edit view of the current user's profile.
    """
    form_class = ProfileEditForm
    model = Profile
    template_name = 'profile/signup_setup.html'
    success_url = reverse_lazy('profile_dashboard')

    def get_object(self, queryset=None):
        return self.request.user.profile


class CustomSignupView(SignupView):
    """
    A subclass of SignupView that uses our custom signup form.
    """
    form_class = CustomSignupForm

    # Use the same template name as django.contrib.auth
    template_name = 'registration/signup.html'
