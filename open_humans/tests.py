from django.contrib import auth
from django.db import IntegrityError
from django.test import TestCase
from django.test.utils import override_settings

from oauth2_provider.models import AccessToken

from common.testing import APITestCase  # , BrowserTestCase

UserModel = auth.get_user_model()

ANONYMOUS_URLS = [
    '/',
    '/account/login/',
    '/account/password/reset/',
    '/account/signup/',
]

AUTHENTICATED_OR_ANONYMOUS_URLS = [
    '/about/',
    '/activities/',
    '/community-guidelines/',
    '/contact-us/',
    '/copyright/',
    '/data-use/',
    '/faq/',
    '/member/beau/',
    '/members/',
    '/members/page/1/',
    '/members/?sort=username',
    '/members/page/1/?sort=username',
    '/public-data/',
    '/public-data/consent/',
    '/news/',
    '/research/',
    '/statistics/',
    '/terms/',
]

REDIRECT_URLS = [
    '/account/delete/',
    '/member/beau/email/',
    '/member/me/',
    '/member/me/account-settings/',
    '/member/me/change-email/',
    '/member/me/change-name/',
    '/member/me/connections/',
    # '/member/me/connections/delete/1/',
    '/member/me/edit/',
    '/member/me/research-data/',
    '/member/me/research-data/data-selfie/',
    # '/member/me/research-data/data-selfie/edit/1/',
    # '/member/me/research-data/data-selfie/delete/1/',
    '/member/me/research-data/delete/pgp/',
    '/member/me/research-data/delete/american_gut/',
    '/member/me/research-data/delete/go_viral/',
    '/member/me/research-data/delete/runkeeper/',
    '/member/me/research-data/delete/twenty_three_and_me/',
    # '/member/me/send-confirmation-email/',
    # '/member/me/study-grants/delete/1/',
    '/public-data/enroll-1-overview/',
    '/public-data/enroll-2-consent/',
    # require a POST
    # '/public-data/enroll-3-quiz/',
    # '/public-data/enroll-4-signature/',
    # 301 redirect
    # '/public-data/toggle-sharing/',
    '/public-data/withdraw/',
    '/welcome/',
    '/welcome/connecting/',
    '/welcome/data-import/',
    '/welcome/enrollment/',
    '/welcome/profile/',
]

AUTHENTICATED_URLS = REDIRECT_URLS + [
    '/account/password/',
]


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
class SmokeTests(TestCase):
    """
    A simple GET test for all of the simple URLs in the site.
    """

    fixtures = ['open_humans/fixtures/test-data.json']

    def test_get_all_simple_urls(self):
        for url in AUTHENTICATED_OR_ANONYMOUS_URLS + ANONYMOUS_URLS:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200,
                             msg='{} returned {}'.format(url,
                                                         response.status_code))

    def test_login_redirect(self):
        for url in REDIRECT_URLS:
            response = self.client.get(url)
            self.assertRedirects(
                response,
                '/account/login/?next={}'.format(url),
                msg_prefix='{} did not redirect to login URL'.format(url))

    def test_all_urls_with_login(self):
        login = self.client.login(username='beau', password='test')
        self.assertEqual(login, True)

        for url in AUTHENTICATED_URLS + AUTHENTICATED_OR_ANONYMOUS_URLS:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200,
                             msg='{} returned {}'.format(url,
                                                         response.status_code))

    def test_redirect_auth_home(self):
        login = self.client.login(username='beau', password='test')
        self.assertEqual(login, True)
        response = self.client.get('/')
        self.assertRedirects(response, '/welcome/')


@override_settings(SSLIFY_DISABLE=True)
class OpenHumansUserTests(TestCase):
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


# We ran out of free BrowserStack time but need to make a decision about either
# paying for BrowserStack or working with them to use their free plan for
# nonprofits. These tests are very useful for verifying important functionality
# like creating an account and logging into the site.
#
# class OpenHumansBrowserTests(BrowserTestCase):
#     """
#     Browser tests of general Open Humans functionality.
#     """

#      def test_create_user(self):
#          driver = self.driver

#         driver.get(self.live_server_url)

#         driver.find_element_by_link_text('Become a member').click()

#         driver.find_element_by_id('signup-username').clear()
#         driver.find_element_by_id('signup-username').send_keys('test_123')

#         driver.find_element_by_id('signup-name').clear()
#         driver.find_element_by_id('signup-name').send_keys('Test Testerson')

#         driver.find_element_by_id('email-address').clear()
#         driver.find_element_by_id('email-address').send_keys(
#             'test@example.com')

#         driver.find_element_by_id('signup-password').clear()
#         driver.find_element_by_id('signup-password').send_keys('testing123')

#         driver.find_element_by_id('signup-password-confirm').clear()
#         driver.find_element_by_id('signup-password-confirm').send_keys(
#             'testing123')

#         driver.find_element_by_name('terms').click()

#         driver.find_element_by_id('create-account').click()

#         self.assertEqual(
#             'Please verify your email address',
#             driver.find_element_by_css_selector('h3.panel-title').text)
