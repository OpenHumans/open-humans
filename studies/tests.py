import factory

from django.db.models import signals
from django.test.utils import override_settings

from rest_framework.test import APITestCase


@override_settings(SSLIFY_DISABLE=True)
class StudyTestCase(APITestCase):
    """
    A helper for writing study tests.
    """

    fixtures = ['open_humans/fixtures/test-data.json']

    @factory.django.mute_signals(signals.post_save)
    def verify_request(self, url, method='get', data=None, status=200):
        args = ['/api' + self.base_url + url]

        if method == 'post':
            args.append(data)

        response = getattr(self.client, method)(*args)

        self.assertEqual(response.status_code, status)
