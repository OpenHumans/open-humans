import json

from django.test import TestCase
from django.test.utils import override_settings


@override_settings(SSLIFY_DISABLE=True)
class DeauthorizationTests(TestCase):
    """
    Simple tests for all of the activity URLs in the site.
    """

    fixtures = ['open_humans/fixtures/test-data.json']

    def test_deauth_with_data_deletion(self):
        self.client.post('/activity/runkeeper/deauthorize/',
                         json.dumps({
                             'access_token': 'example-access-token-7',
                             'delete_health': True,
                         }),
                         content_type='application/json')
