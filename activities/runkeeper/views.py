import json

from django.http import (HttpResponseBadRequest, HttpResponseNotFound,
                         HttpResponse)
from django.views.generic import View

from social.apps.django_app.default.models import UserSocialAuth

from data_import.models import DataFile


class DeauthorizeView(View):
    """
    A view called by RunKeeper any time a user deactivates their RunKeeper
    account.
    """

    @staticmethod
    def post(request):
        try:
            data = json.loads(request.body)
        except ValueError:
            return HttpResponseBadRequest()

        if 'access_token' not in data:
            return HttpResponseBadRequest()

        try:
            user_social_auth = UserSocialAuth.objects.get(
                provider='runkeeper',
                extra_data__contains='"access_token": "{}"'.format(
                    data['access_token']))
        except UserSocialAuth.DoesNotExist:
            return HttpResponseNotFound()

        user = user_social_auth.user

        if 'delete_health' in data and data['delete_health']:
            data = DataFile.objects.filter(
                user=user, source='runkeeper')
            data.delete()

        user.runkeeper.disconnect()

        return HttpResponse()
