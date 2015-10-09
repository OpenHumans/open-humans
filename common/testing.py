import json
import logging
import os
import subprocess
import sys
import time

import factory

from django.db.models import signals
from django.test import LiveServerTestCase
from django.test.utils import override_settings

from rest_framework.test import APITestCase as BaseAPITestCase
from selenium import webdriver

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


def short_hash():
    """
    Return the current git commit or `None`.
    """
    try:
        return (subprocess.check_output(
            ['git', 'rev-parse', '--short', 'HEAD']).strip())
    except:
        return None


class BrowserTestCase(LiveServerTestCase):
    """
    A test case that runs via BrowserStack.
    """

    @classmethod
    def setUpClass(cls):
        super(BrowserTestCase, cls).setUpClass()

        cls.capabilities = {
            'browser': 'Chrome',
            'browser_version': '45.0',
            # 'browserstack.debug': True,
            'browserstack.local': True,
            'browserstack.selenium_version': '2.47.1',
            'build': short_hash(),
            'os': 'Windows',
            'os_version': '10',
            'resolution': '1920x1080'
        }

        os_name = 'osx' if sys.platform == 'darwin' else 'linux'

        # Run BrowserStackLocal
        cls.local = subprocess.Popen(
            [
                './bin/BrowserStackLocal-{}'.format(os_name),
                os.getenv('BROWSERSTACK_KEY'),
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)

        # Wait for initialization (could be improved)
        time.sleep(5)

        cls.driver = webdriver.Remote(
            command_executor=os.getenv('COMMAND_EXECUTOR'),
            desired_capabilities=cls.capabilities)

        cls.driver.maximize_window()

        cls.driver.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

        cls.local.send_signal(subprocess.signal.SIGINT)

        super(BrowserTestCase, cls).tearDownClass()
