from cStringIO import StringIO

from account.models import EmailConfirmation

from django.contrib import auth
from django.core import management
from django.db import IntegrityError
from django.test import TestCase
from django.test.utils import override_settings
from django.utils import timezone

from mock import patch
from oauth2_provider.models import AccessToken

from common.api_testing import APITestCase
from common.testing import BrowserTestCase, get_or_create_user, SmokeTestCase

from .models import Member

UserModel = auth.get_user_model()


class BasicAPITests(APITestCase):
    """
    Test the basic API URLs.
    """

    def test_get_member(self):
        """
        Ensure we can get a UserData object with credentials.
        """
        access_token = AccessToken.objects.filter(user__username='beau')[0]

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


class SmokeTests(SmokeTestCase):
    """
    A simple GET test for all of the simple URLs in the site.
    """

    anonymous_urls = [
        '/account/login/',
        '/account/password/reset/',
        '/account/signup/',
    ]

    authenticated_or_anonymous_urls = [
        '/',
        '/about/',
        '/api/public-data/?username=beau',
        '/api/public-data/?created_start=2/14/2016&created_end=2/14/2016',
        '/api/public-data/sources-by-member/',
        '/api/public-data/members-by-source/',
        '/beau/',
        '/community-guidelines/',
        '/contact-us/',
        '/copyright/',
        '/data-use/',
        '/member/beau/',
        '/members/',
        '/members/page/1/',
        '/members/?sort=username',
        '/members/page/1/?sort=username',
        '/public-data/',
        '/public-data/consent/',
        '/public-data-api/',
        '/news/',
        '/research/',
        '/terms/',
    ]

    redirect_urls = [
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
        '/member/me/research-data/delete/pgp/',
        '/member/me/research-data/delete/american_gut/',
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
    ]

    authenticated_urls = redirect_urls + [
        '/account/password/',
        ('/oauth2/authorize/?origin=external&response_type=code'
         '&scope=go-viral%20read%20write&client_id=example-id-15'),
    ]

    def test_custom_404(self):
        self.assert_status_code('/does-not-exist/', status_code=404)

    def test_custom_500(self):
        with self.assertRaises(Exception):
            self.assert_status_code('/raise-exception/', status_code=500)


@override_settings(SSLIFY_DISABLE=True)
class OpenHumansUserTests(TestCase):
    """
    Tests for our custom User class.
    """

    def setUp(self):  # noqa
        get_or_create_user('user1')

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


class CommandTests(TestCase):
    """
    Tests for our management commands.
    """

    fixtures = ['open_humans/fixtures/test-data.json']

    def setUp(self):
        self.output = StringIO()

    def test_bulk_email(self):
        try:
            import sys
            out, sys.stdout = sys.stdout, StringIO()
            management.call_command('bulk_email', '-h', stdout=self.output)
            sys.stdout = out
        except SystemExit as e:
            if e.code != 0:
                raise e

    def test_bulk_tasks(self):
        management.call_command('bulk_tasks', '--app=pgp', stdout=self.output)
        management.call_command('bulk_tasks', '--app=pgp', '--user=beau',
                                stdout=self.output)

    def test_setup_api(self):
        management.call_command('setup_api', stdout=self.output)

    def test_update_badges(self):
        management.call_command('update_badges', stdout=self.output)

    def test_user_connections_json(self):
        management.call_command('user_connections_json', '/dev/null',
                                stdout=self.output)

    def test_stats(self):
        management.call_command('stats', '--days=365', stdout=self.output)


class WsgiTests(TestCase):
    """
    Tests for our WSGI application.
    """

    @staticmethod
    def test_import():
        from .wsgi import application  # noqa, pylint: disable=unused-variable


class WelcomeEmailTests(TestCase):
    """
    Tests for our welcome email.
    """

    @patch('open_humans.signals.send_mail')
    def test_send_welcome_email(self, mock):
        user = get_or_create_user('email_test_user')

        member = Member(user=user)
        member.save()

        email = user.emailaddress_set.all()[0]
        email.verified = False
        email.save()

        confirmation = EmailConfirmation.create(email)
        confirmation.sent = timezone.now()
        confirmation.save()

        # confirm the email; this sends the email_confirmed signals
        confirmed_email = confirmation.confirm()

        self.assertTrue(confirmed_email is not None)
        self.assertTrue(mock.called)
        self.assertEqual(mock.call_count, 1)
        self.assertEqual(mock.call_args[0][-1][0], u'email_test_user@test.com')


class OpenHumansBrowserTests(BrowserTestCase):
    """
    Browser tests of general Open Humans functionality.
    """

    def test_create_user(self):
        driver = self.driver

        driver.get(self.live_server_url)

        driver.find_element_by_class_name('signup-link').click()

        username = self.wait_for_element_id('signup-username')

        username.clear()
        username.send_keys('test_123')

        name = driver.find_element_by_id('signup-name')

        name.clear()
        name.send_keys('Test Testerson')

        email = driver.find_element_by_id('email-address')

        email.clear()
        email.send_keys('test@example.com')

        password = driver.find_element_by_id('signup-password')

        password.clear()
        password.send_keys('testing123')

        password_confirm = driver.find_element_by_id('signup-password-confirm')

        password_confirm.clear()
        password_confirm.send_keys('testing123')

        driver.find_element_by_name('terms').click()

        driver.find_element_by_id('create-account').click()

        self.assertEqual(
            'Please verify your email address.',
            driver.find_element_by_css_selector(
                '.call-to-action-3 > .container > h3').text)

    def test_remove_connection(self):
        driver = self.driver

        self.login()

        driver.get(self.live_server_url + '/member/me/connections/')

        driver.find_element_by_xpath(
            "(//a[contains(text(),'Remove connection')])[1]").click()
        driver.find_element_by_name('remove_datafiles').click()
        driver.find_element_by_css_selector('label').click()
        driver.find_element_by_css_selector('input.btn.btn-danger').click()
