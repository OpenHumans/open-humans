from django.contrib import auth
from django.db import IntegrityError
from django.test import SimpleTestCase
from django.test.utils import override_settings

from oauth2_provider.models import AccessToken

from common.testing import APITestCase

UserModel = auth.get_user_model()


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
            '/account/login/',
            '/account/signup/',
            '/community-guidelines/',
            '/contact-us/',
            '/data-use/',
            '/members/',
            '/terms/',
        ]

        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)

    def test_login_redirect(self):
        urls = [
            '/member/me/',
            '/member/me/change-email/',
            '/member/me/change-name/',
            '/member/me/edit/',
            '/member/me/research-data/',
            '/member/me/research-data/delete/5/',
            '/member/me/send-confirmation-email/',
        ]

        for url in urls:
            response = self.client.get(url)
            self.assertRedirects(response, '/account/login/?next={}'.format(
                url))


@override_settings(SSLIFY_DISABLE=True)
class OpenHumansUserTests(SimpleTestCase):
    """
    Tests for our custom User class.
    """

    def setUp(self):  # noqa
        try:
            UserModel.objects.get(username='user1')
        except UserModel.DoesNotExist:
            UserModel.objects.create_user('user1', 'user1@test.com', 'user1')

    def test_lookup_by_username(self):
        user1 = auth.authenticate(username='user1', password='user1')

        self.assertEqual(user1.username, 'user1')

    def test_lookup_by_email(self):
        user1 = auth.authenticate(username='user1@test.com', password='user1')

        self.assertEqual(user1.username, 'user1')

    def test_lowercase_unique(self):
        # Create a lowercase user2
        UserModel.objects.create_user('user2', 'user2@test.com', 'user2')

        # Creating an uppercase USER2 should fail
        self.assertRaises(IntegrityError, UserModel.objects.create_user,
                          'USER2', 'other+user2@test.com', 'user2')
