from datetime import datetime, timedelta
from urllib import quote

from django.contrib import auth
from django.test import TestCase
from django.test.utils import override_settings

from oauth2_provider.models import AccessToken

from common.testing import BrowserTestCase, get_or_create_user, SmokeTestCase
from open_humans.models import Member

from .models import (DataRequestProjectMember, OnSiteDataRequestProject,
                     OAuth2DataRequestProject)

UserModel = auth.get_user_model()


class DirectSharingMixin(object):
    """
    Mixins for both types of direct sharing tests.
    """

    fixtures = SmokeTestCase.fixtures + [
        'private_sharing/fixtures/test-data.json',
    ]

    @staticmethod
    def setUp():
        """
        Delete all ProjectMembers so tests don't rely on each others' state.
        """
        DataRequestProjectMember.objects.all().delete()

    def update_member(self, joined, authorized):
        # first delete the ProjectMember
        try:
            project_member = DataRequestProjectMember.objects.get(
                member=self.member1,
                project=self.member1_project)

            project_member.delete()
        except DataRequestProjectMember.DoesNotExist:
            pass

        # then re-create it
        project_member = DataRequestProjectMember(
            member=self.member1,
            project=self.member1_project,
            joined=joined,
            authorized=authorized,
            sources_shared=self.member1_project.request_sources_access,
            username_shared=self.member1_project.request_username_access,
            message_permission=self.member1_project.request_message_permission)

        project_member.save()


@override_settings(SSLIFY_DISABLE=True)
class DirectSharingOnSiteTests(DirectSharingMixin, TestCase):
    """
    Tests for private sharing on-site projects.
    """

    @classmethod
    def setUpClass(cls):
        super(DirectSharingOnSiteTests, cls).setUpClass()

        cls.join_url = '/direct-sharing/projects/on-site/join/abc-2/'
        cls.authorize_url = '/direct-sharing/projects/on-site/authorize/abc-2/'

        user1 = get_or_create_user('user1')
        cls.member1, _ = Member.objects.get_or_create(user=user1)
        cls.member1_project = OnSiteDataRequestProject.objects.get(
            slug='abc-2')
        email1 = cls.member1.primary_email

        email1.verified = True
        email1.save()

    def test_join_if_logged_out(self):
        response = self.client.get(self.join_url)

        self.assertRedirects(response, '/account/login/?next={}'.format(
            self.join_url))

    def test_join_if_logged_in(self):
        login = self.client.login(username='user1', password='user1')
        self.assertTrue(login)

        response = self.client.get(self.join_url)

        self.assertEqual(response.status_code, 200)

    def test_authorize_if_logged_out(self):
        response = self.client.get(self.authorize_url)

        self.assertRedirects(response, '/account/login/?next={}'.format(
            self.authorize_url))

    def test_authorize_if_logged_in_and_not_joined(self):
        login = self.client.login(username='user1', password='user1')
        self.assertTrue(login)

        self.update_member(joined=False, authorized=False)

        response = self.client.get(self.authorize_url)

        self.assertRedirects(response, self.join_url)

    def test_join_if_already_joined(self):
        login = self.client.login(username='user1', password='user1')
        self.assertTrue(login)

        self.update_member(joined=True, authorized=False)

        response = self.client.get(self.join_url)

        self.assertRedirects(response, self.authorize_url)

    def test_authorize_if_already_joined(self):
        login = self.client.login(username='user1', password='user1')
        self.assertTrue(login)

        self.update_member(joined=True, authorized=False)

        response = self.client.get(self.authorize_url)

        self.assertEqual(response.status_code, 200)

    def test_join_if_already_authorized(self):
        login = self.client.login(username='user1', password='user1')
        self.assertTrue(login)

        self.update_member(joined=True, authorized=True)

        response = self.client.get(self.join_url)

        self.assertRedirects(response, self.authorize_url)

    def test_authorize_if_already_authorized(self):
        login = self.client.login(username='user1', password='user1')
        self.assertTrue(login)

        self.update_member(joined=True, authorized=True)

        response = self.client.get(self.authorize_url)

        self.assertEqual(
            'Project previously authorized.' in response.content, True)


@override_settings(SSLIFY_DISABLE=True)
class DirectSharingOAuth2Tests(DirectSharingMixin, TestCase):
    """
    Tests for private sharing OAuth2 projects.
    """

    @classmethod
    def setUpClass(cls):
        super(DirectSharingOAuth2Tests, cls).setUpClass()

        cls.authorize_url = ('/direct-sharing/projects/oauth2/authorize/'
                             '?client_id=test-key&response_type=code')

        user1 = get_or_create_user('user1')
        cls.member1, _ = Member.objects.get_or_create(user=user1)
        cls.member1_project = OAuth2DataRequestProject.objects.get(
            slug='abc')
        email1 = cls.member1.primary_email

        cls.access_token = AccessToken(
            application=cls.member1_project.application,
            user=user1,
            token='test-token-1',
            expires=datetime.now() + timedelta(days=1),
            scope='read')
        cls.access_token.save()

        email1.verified = True
        email1.save()

    def test_authorize_if_logged_out(self):
        response = self.client.get(self.authorize_url)

        self.assertRedirects(
            response,
            '/account/login/oauth2?connection=abc&next={}'.format(
                quote(self.authorize_url, safe='')))

    def test_authorize_if_logged_in(self):
        login = self.client.login(username='user1', password='user1')
        self.assertTrue(login)

        self.update_member(joined=False, authorized=False)

        response = self.client.get(self.authorize_url)

        self.assertEqual(response.status_code, 200)

    def test_authorize_if_already_authorized(self):
        login = self.client.login(username='user1', password='user1')
        self.assertTrue(login)

        self.update_member(joined=True, authorized=True)

        response = self.client.get(self.authorize_url)

        self.assertTrue(
            'Project previously authorized.' in response.content)

    def test_access_token_to_project_member(self):
        self.update_member(joined=True, authorized=True)

        project_member = DataRequestProjectMember.objects.get(
            project=self.member1_project,
            member=self.member1)

        response = self.client.get(
            '/api/direct-sharing/project/exchange-member/'
            '?access_token=test-token-1')

        json = response.json()

        self.assertTrue(
            json['project_member_id'] == project_member.project_member_id)
        self.assertTrue(json['username'] == 'user1')
        self.assertTrue(json['username_shared'] is True)
        self.assertTrue(json['message_permission'] is True)
        self.assertTrue(json['message_permission'] is True)

        self.assertTrue(len(json['sources_shared']) == 4)

        self.assertTrue('american_gut' in json['sources_shared'])
        self.assertTrue('ancestry_dna' in json['sources_shared'])
        self.assertTrue('data_selfie' in json['sources_shared'])
        self.assertTrue('twenty_three_and_me' in json['sources_shared'])

    def test_oauth2_authorize(self):
        login = self.client.login(username='user1', password='user1')
        self.assertTrue(login)

        response = self.client.get(self.authorize_url)

        data = {
            'redirect_uri': 'http://localhost:8001/oauth-authorize',
            'scope': 'read',
            'client_id': 'test-key',
            'state': '',
            'response_type': 'code',
            'allow': 'Authorize project',
        }

        response = self.client.post(self.authorize_url, data=data)

        self.assertIn('http://localhost:8001/oauth-authorize?code=',
                      response.url)

        code = (response.url
                .replace('http://localhost:8001/oauth-authorize?code=', '')
                .replace('&origin=external', ''))

        data = {
            'client_id': 'test-key',
            'client_secret': 'test-secret',
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': 'http://localhost:8001/oauth-authorize',
        }

        response = self.client.post('/oauth2/token/', data=data)

        json = response.json()

        self.assertIn('access_token', json)
        self.assertIn('refresh_token', json)

        self.assertEqual(json['expires_in'], 36000)
        self.assertEqual(json['scope'], 'read')
        self.assertEqual(json['token_type'], 'Bearer')


class SmokeTests(SmokeTestCase):
    """
    A simple GET test for all of the simple URLs in the site.
    """

    on_site_master_token = 'def456'
    oauth2_master_token = 'abc123'

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

        '/api/direct-sharing/project/?access_token={0}'.format(
            on_site_master_token),
        '/api/direct-sharing/project/?access_token={0}'.format(
            oauth2_master_token),

        '/api/direct-sharing/project/members/?access_token={0}'.format(
            on_site_master_token),
        '/api/direct-sharing/project/members/?access_token={0}'.format(
            oauth2_master_token),
    ]

    fixtures = SmokeTestCase.fixtures + [
        'private_sharing/fixtures/test-data.json',
    ]


class BrowserTests(BrowserTestCase):
    """
    Browser tests of direct sharing functionality.
    """

    fixtures = BrowserTestCase.fixtures + [
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

    def test_create_on_site(self):
        driver = self.driver

        self.login()

        driver.get(self.live_server_url + '/direct-sharing/projects/manage/')

        driver.find_element_by_link_text(
            'Create a new on-site data request project').click()

        driver.find_element_by_id('id_is_study_1').click()

        driver.find_element_by_css_selector('div.radio > label').click()

        driver.find_element_by_id('id_name').clear()
        driver.find_element_by_id('id_name').send_keys('Test Study')

        driver.find_element_by_id('id_leader').clear()
        driver.find_element_by_id('id_leader').send_keys('Beau Gunderson')

        driver.find_element_by_id('id_organization').clear()
        driver.find_element_by_id('id_organization').send_keys('N/A')

        driver.find_element_by_id('id_is_academic_or_nonprofit_1').click()

        driver.find_element_by_id('id_contact_email').clear()
        driver.find_element_by_id('id_contact_email').send_keys(
            'beau@beaugunderson.com')

        driver.find_element_by_id('id_info_url').clear()
        driver.find_element_by_id('id_info_url').send_keys(
            'https://beaugunderson.com/')

        driver.find_element_by_id('id_short_description').clear()
        driver.find_element_by_id('id_short_description').send_keys(
            'Just testing!')

        driver.find_element_by_id('id_long_description').clear()
        driver.find_element_by_id('id_long_description').send_keys(
            'Just testing!')

        driver.find_element_by_id('id_badge_image').clear()
        driver.find_element_by_id('id_badge_image').send_keys(
            '/Users/beau/Documents/TwitterHeader.jpg')

        driver.find_element_by_id('id_request_sources_access_1').click()
        driver.find_element_by_id('id_request_sources_access_2').click()
        driver.find_element_by_id('id_request_sources_access_3').click()
        driver.find_element_by_id('id_request_sources_access_4').click()
        driver.find_element_by_id('id_request_sources_access_5').click()
        driver.find_element_by_id('id_request_sources_access_6').click()
        driver.find_element_by_id('id_request_sources_access_7').click()
        driver.find_element_by_id('id_request_sources_access_8').click()
        driver.find_element_by_id('id_request_sources_access_9').click()
        driver.find_element_by_id('id_request_sources_access_10').click()
        driver.find_element_by_id('id_request_sources_access_11').click()
        driver.find_element_by_id('id_request_sources_access_12').click()
        driver.find_element_by_id('id_request_sources_access_13').click()

        driver.find_element_by_id('id_request_message_permission_1').click()

        driver.find_element_by_id('id_request_username_access_1').click()

        driver.find_element_by_id('id_consent_text').clear()
        driver.find_element_by_id('id_consent_text').send_keys(
            '## Consent form\n\n- list item 1\n- list item 2\n- list item 3')

        driver.find_element_by_id('id_post_sharing_url').clear()
        driver.find_element_by_id('id_post_sharing_url').send_keys(
            'https://beaugunderson.com/?id=OH_PROJECT_MEMBER_ID')

        driver.find_element_by_id('create-project').click()

        self.assertEqual('Test Study', driver.find_element_by_xpath(
            "//table[@id='on-site-projects']/tbody/tr[1]/td").text)
