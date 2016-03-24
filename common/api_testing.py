import json
import logging

import factory

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
    def verify_request(self, url, method='get', body=None, status=200):
        args = ['/api' + self.base_url + url]

        if method in ['post', 'patch', 'put']:
            args.append(body)

        logger.debug('%s %s', method.upper(), args)

        response = getattr(self.client, method)(*args)

        self.assertEqual(response.status_code, status)

        if method == 'get' and body:
            self.assertEqual(json.loads(response.content), body)

        try:
            return json.loads(response.content)
        except ValueError:
            pass
