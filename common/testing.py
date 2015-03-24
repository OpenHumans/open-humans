import factory
import logging

from django.db.models import signals
from django.test.utils import override_settings

from rest_framework.test import APITestCase as BaseAPITestCase

logger = logging.getLogger(__name__)


@override_settings(SSLIFY_DISABLE=True)
class APITestCase(BaseAPITestCase):
    """
    A helper for writing study tests.
    """

    base_url = ''
    fixtures = ['open_humans/fixtures/test-data.json']

    @factory.django.mute_signals(signals.post_save)
    def verify_request(self, url, method='get', data=None, status=200):
        args = ['/api' + self.base_url + url]

        if method == 'post':
            args.append(data)

        logger.debug('%s %s', method.upper(), args[0])

        response = getattr(self.client, method)(*args)

        self.assertEqual(response.status_code, status)
