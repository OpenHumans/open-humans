from django.test import SimpleTestCase
from django.test.utils import override_settings

from oauth2_provider.models import AccessToken

from common.testing import APITestCase


class BasicAPITests(APITestCase):
    """
    Test the basic API URLs.
    """

    def test_get_member(self):
        """
        Ensure we can get a UserData object with credentials.
        """
        access_token = AccessToken.objects.get(pk=1)

        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + access_token.token)

        self.verify_request('/member/')
        self.verify_request('/member/', method='post', status=405)
        self.verify_request('/member/', method='delete', status=405)

    def test_get_member_no_credentials(self):
        """
        Ensure we can't get a UserData object with no credentials.
        """
        self.client.credentials()

        self.verify_request('/member/', status=401)
        self.verify_request('/member/', method='post', status=401)
        self.verify_request('/member/', method='delete', status=401)


@override_settings(SSLIFY_DISABLE=True)
class SmokeTests(SimpleTestCase):
    """
    A simple GET test for all of the simple URLs in the site.
    """

    def test_get_all_simple_urls(self):
        urls = [
            '/',
            '/about/',
            '/community_guidelines/',
            '/contact-us/',
            '/data-use/',
            '/public-data/',
            '/terms/',
        ]

        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
