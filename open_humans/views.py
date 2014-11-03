from datetime import datetime
import json
import os

import requests

from account.views import SignupView

from django.conf import settings
from django.contrib import messages
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponse
from django.views.generic.base import RedirectView, View
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView
from django.views.generic.list import ListView
from django.core.files.storage import default_storage

from activities.twenty_three_and_me.models import ActivityDataFile as ActivityDataFile23andme

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


class DatasetsView(ListView):
    model = ActivityDataFile23andme
    template_name = "profile/research_data.html"
    context_object_name = 'data_sets'

    def get_queryset(self):
        return ActivityDataFile23andme.objects.filter(study_user__user=self.request.user)


class JSONDataView(View):
    """
    A view that returns JSON data.
    """

    def get(self, request):
        data = self.get_data(request, data_type=request.GET['data_type'])
        return HttpResponse(json.dumps(data),
                            content_type='application/json')

    def get_data(self, request, data_type):
        if data_type == '23andme_names':
            access_token = request.user.social_auth.get(provider='23andme').extra_data['access_token']
            headers = {'Authorization': 'Bearer %s' % access_token}
            names_req = requests.get("https://api.23andme.com/1/names/",
                                     headers=headers, verify=False)
            if names_req.status_code == 200:
                return names_req.json()
        return None


class ExceptionView(View):
    """
    Raises an exception for testing purposes.
    """
    def get(self, request):
        raise Exception('A test exception.')
