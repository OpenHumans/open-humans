from django.test import TestCase
from django.test.utils import override_settings

AUTHENTICATED_URLS = [
    '/activity/23andme/upload/',
    '/activity/ancestry-dna/upload/',
    '/activity/data-selfie/upload/',
    '/activity/moves/finalize-import/',
    # '/activity/runkeeper/disconnect/',
    '/activity/runkeeper/finalize-import/',
    # '/activity/runkeeper/request-data-retrieval/',
]


@override_settings(SSLIFY_DISABLE=True)
class SmokeTests(TestCase):
    """
    Simple tests for all of the activity URLs in the site.
    """

    fixtures = ['open_humans/fixtures/test-data.json']

    def test_login_redirect(self):
        for url in AUTHENTICATED_URLS:
            response = self.client.get(url)

            self.assertRedirects(
                response,
                '/account/login/?next={}'.format(url),
                msg_prefix='{} did not redirect to login URL'.format(url))

    def test_all_urls_with_login(self):
        login = self.client.login(username='beau', password='test')
        self.assertEqual(login, True)

        for url in AUTHENTICATED_URLS:
            response = self.client.get(url)

            self.assertEqual(
                response.status_code, 200, msg='{} returned {}'.format(
                    url, response.status_code))
