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
                if 'profile_id' not in request.POST:
                    messages.error(request, "Please select a profile.")
                    self.url = reverse_lazy('profile_research_data_complete_23andme')
                else:
                    # get_upload_path creates locations for files in
                    # ActivityDataFile23andme (i.e. its the "upload_to" arg).
                    study_user, _ = ActivityUser23andme.objects.get_or_create(user=request.user)
                    userdata = ActivityDataFile23andMe(study_user=study_user)
                    filename = '23andme-%s.tar.bz2' % (datetime.now().strftime("%Y%m%d%H%M%S"))
                    s3_key_name = get_upload_path(userdata, filename)

                    # Ask Flask app to put together this dataset.
                    url = 'https://oh-data-extraction-staging.herokuapp.com/23andme'
                    access_token = request.user.social_auth.get(provider='23andme').extra_data['access_token']
                    data_extraction_params = {
                        'access_token': access_token,
                        'profile_id': request.POST['profile_id'],
                        's3_key_name': s3_key_name
                        }
                    requests.get(url,  params=data_extraction_params)

                    # Update with the expected file location.
                    userdata.file.name = s3_key_name
                    userdata.save()
                    message = ("Thanks! We've started the data import " +
                               "for your 23andme data from profile.")
                    messages.success(request, message)
        return super(RequestDataExportView, self).post(request)
