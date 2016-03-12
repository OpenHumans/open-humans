from django.contrib import auth
from django.test import TestCase
from django.test.utils import override_settings

from common.testing import BrowserTestCase, get_or_create_user, SmokeTestCase
from open_humans.models import Member

from .models import DataRequestProjectMember, OnSiteDataRequestProject

UserModel = auth.get_user_model()


@override_settings(SSLIFY_DISABLE=True)
class PrivateSharingTests(TestCase):
    """
    Tests for private sharing.
    """

    fixtures = SmokeTestCase.fixtures + [
        'private_sharing/fixtures/test-data.json',
    ]

    @classmethod
    def setUpClass(cls):
        super(PrivateSharingTests, cls).setUpClass()

        cls.join_url = '/direct-sharing/projects/on-site/join/abc-2/'
        cls.authorize_url = '/direct-sharing/projects/on-site/authorize/abc-2/'

        user1 = get_or_create_user('user1')
        cls.member1, _ = Member.objects.get_or_create(user=user1)
        cls.member1_project = OnSiteDataRequestProject.objects.get(slug='abc-2')
        email1 = cls.member1.primary_email

        email1.verified = True
        email1.save()

    def update_member(self, joined, authorized):
        # first delete the ProjectMember
        try:
            project_member = DataRequestProjectMember.objects.get(
                member=self.member1, project=self.member1_project)
            project_member.delete()
        except DataRequestProjectMember.DoesNotExist:
            pass

        # then re-create it
        if joined:
            project_member = DataRequestProjectMember(
                member=self.member1, project=self.member1_project)

            project_member.authorized = authorized

            project_member.save()

    def test_join_if_logged_out(self):
        response = self.client.get(self.join_url)

        self.assertRedirects(response, '/account/login/?next={}'.format(
            self.join_url))

    def test_join_if_logged_in(self):
        login = self.client.login(username='user1', password='user1')
        self.assertEqual(login, True)

        response = self.client.get(self.join_url)

        self.assertEqual(response.status_code, 200)

    def test_authorize_if_logged_out(self):
        response = self.client.get(self.authorize_url)

        self.assertRedirects(response, '/account/login/?next={}'.format(
            self.authorize_url))

    def test_authorize_if_logged_in_and_not_joined(self):
        login = self.client.login(username='user1', password='user1')
        self.assertEqual(login, True)

        self.update_member(joined=False, authorized=False)

        response = self.client.get(self.authorize_url)

        self.assertRedirects(response, self.join_url)

    def test_join_if_already_joined(self):
        login = self.client.login(username='user1', password='user1')
        self.assertEqual(login, True)

        self.update_member(joined=True, authorized=False)

        response = self.client.get(self.join_url)

        self.assertRedirects(response, self.authorize_url)

    def test_authorize_if_already_joined(self):
        login = self.client.login(username='user1', password='user1')
        self.assertEqual(login, True)

        self.update_member(joined=True, authorized=False)

        response = self.client.get(self.authorize_url)

        self.assertEqual(response.status_code, 200)

    def test_join_if_already_authorized(self):
        login = self.client.login(username='user1', password='user1')
        self.assertEqual(login, True)

        self.update_member(joined=True, authorized=True)

        response = self.client.get(self.join_url)

        self.assertRedirects(response, self.authorize_url)

    def test_authorize_if_already_authorized(self):
        login = self.client.login(username='user1', password='user1')
        self.assertEqual(login, True)

        self.update_member(joined=True, authorized=True)

        response = self.client.get(self.authorize_url)

        self.assertEqual(
            'Project previously authorized.' in response.content, True)


class SmokeTests(SmokeTestCase):
    """
    A simple GET test for all of the simple URLs in the site.
    """

    authenticated_urls = [
        '/direct-sharing/projects/manage/',
        '/direct-sharing/projects/oauth2/create/',
        '/direct-sharing/projects/oauth2/update/abc/',
        '/direct-sharing/projects/oauth2/abc/',
        '/direct-sharing/projects/on-site/create/',
        '/direct-sharing/projects/on-site/update/abc-2/',
        '/direct-sharing/projects/on-site/abc-2/',
    ]

    authenticated_or_anonymous_urls = [
        '/direct-sharing/overview/',
    ]

    fixtures = SmokeTestCase.fixtures + [
        'private_sharing/fixtures/test-data.json',
    ]


class BrowserTests(BrowserTestCase):
    """
    Browser tests of direct sharing functionality.
    """

    fixtures = SmokeTestCase.fixtures + [
        'private_sharing/fixtures/test-data.json',
    ]

    def test_join_and_authorize(self):
        driver = self.driver

        self.login()

        driver.get(self.live_server_url +
                   '/direct-sharing/projects/on-site/join/abc-2/')

        self.assertEqual(
            "Join 'abc 2'",
            driver.find_element_by_css_selector('h3.page-header').text)

        driver.find_element_by_id('accept').click()

        self.assertEqual(
            "Authorize 'abc 2'",
            driver.find_element_by_css_selector('h3.page-header').text)

        driver.find_element_by_id('authorize-project').click()

        self.assertEqual(
            ('You have successfully joined the project "abc 2".' in
             driver.find_element_by_css_selector('.message.success').text),
            True)
