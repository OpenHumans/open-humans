from django.test import TestCase
from django.test.utils import override_settings


@override_settings(SSLIFY_DISABLE=True)
class SmokeTests(TestCase):
    """
    A simple GET test for all of the simple URLs in the site.
    """

    def test_get_all_simple_urls(self):
        urls = [
            '/private-sharing/overview/',
            '/private-sharing/apps/create/',
        ]

        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)

    def test_login_redirect(self):
        urls = [
            '/private-sharing/apps/manage/',
            '/private-sharing/apps/oauth2/create/',
            '/private-sharing/apps/oauth2/update/1/',
            '/private-sharing/apps/on-site/create/',
            '/private-sharing/apps/on-site/update/1/',
        ]

        for url in urls:
            response = self.client.get(url)
            self.assertRedirects(response, '/account/login/?next={}'.format(
                url))
