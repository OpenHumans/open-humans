from django.test import TestCase
from django.test.utils import override_settings

AUTHENTICATED_URLS = [
    '/private-sharing/projects/manage/',
    '/private-sharing/projects/oauth2/create/',
    '/private-sharing/projects/oauth2/update/1/',
    '/private-sharing/projects/oauth2/1/',
    '/private-sharing/projects/on-site/create/',
    '/private-sharing/projects/on-site/update/2/',
    '/private-sharing/projects/on-site/2/',
]

AUTHENTICATED_OR_ANONYMOUS_URLS = [
    '/private-sharing/overview/',
]


@override_settings(SSLIFY_DISABLE=True)
class SmokeTests(TestCase):
    """
    A simple GET test for all of the simple URLs in the site.
    """

    fixtures = [
        'open_humans/fixtures/test-data.json',
        'private_sharing/fixtures/test-data.json',
    ]

    def test_get_all_simple_urls(self):
        for url in AUTHENTICATED_OR_ANONYMOUS_URLS:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200,
                             msg='{} returned {}'.format(url,
                                                         response.status_code))

    def test_all_urls_with_login(self):
        login = self.client.login(username='beau', password='test')
        self.assertEqual(login, True)

        for url in AUTHENTICATED_URLS + AUTHENTICATED_OR_ANONYMOUS_URLS:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200,
                             msg='{} returned {}'.format(url,
                                                         response.status_code))


    def test_login_redirect(self):
        for url in AUTHENTICATED_URLS:
            response = self.client.get(url)
            self.assertRedirects(
                response,
                '/account/login/?next={}'.format(url),
                msg_prefix='{} did not redirect to login URL'.format(url))
