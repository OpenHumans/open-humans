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

from .forms import CustomSignupForm, ProfileEditForm
from .models import Profile

from studies.twenty_three_and_me.models import (
    get_upload_path,
    ActivityDataFile as ActivityDataFile23andMe,
    ActivityUser as ActivityUser23andme)


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


class RequestDataExportView(RedirectView):
    """
    Initiate of data export task and redirect to user's data page
    """
    url = reverse_lazy('profile_research_data')

    def post(self, request):
        if 'activity' in request.POST:
            if request.POST['activity'] == '23andme':
                if 'profile_id' in request.POST:
                    # Test initiation of data extraction and associated models.
                    # Local file management to be replaced with S3 management.
                    filename = '23andme-%s.tar.bz2' % (datetime.now().strftime("%Y%m%d%H%M%S"))
                    study_user, _ = ActivityUser23andme.objects.get_or_create(user=request.user)
                    userdata = ActivityDataFile23andMe(study_user=study_user)

                    # To be replaced with file creation by oh-data-extraction.
                    # filepath will become the S3 key name
                    filepath = os.path.join(settings.MEDIA_ROOT, get_upload_path(userdata, filename))
                    print os.path.dirname(filepath)
                    if not os.path.exists(os.path.dirname(filepath)):
                        os.makedirs(os.path.dirname(filepath))
                    with open(filepath, 'w') as file:
                        file.write('This is some test data\n')

                    userdata.file.name = filepath

                    # Testing that we can read this file now.
                    test_data = userdata.file.read()
                    print test_data

                    userdata.save()
                    message = ("Thanks! We've started the data import " +
                               "for your 23andme data from profile id: " +
                               request.POST['profile_id'])
                    messages.success(request, message)
                else:
                    # Reload completion page if no profile selected.
                    messages.error(request, "Please select a profile.")
                    self.url = reverse_lazy('profile_research_data_complete_23andme')
        return super(RequestDataExportView, self).post(request)
