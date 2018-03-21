import os
import unittest

from cStringIO import StringIO
from datetime import datetime, timedelta
from urllib import quote

from django.conf import settings
from django.contrib import auth
from django.test import TestCase
from django.test.utils import override_settings

from oauth2_provider.models import AccessToken

from common.testing import BrowserTestCase, get_or_create_user, SmokeTestCase
from open_humans.models import Member

from .models import (DataRequestProjectMember, OnSiteDataRequestProject,
                     OAuth2DataRequestProject, ProjectDataFile)
from .testing import DirectSharingMixin, DirectSharingTestsMixin

UserModel = auth.get_user_model()


@override_settings(SSLIFY_DISABLE=True)
class DirectSharingOnSiteTests(DirectSharingMixin, DirectSharingTestsMixin,
                               TestCase):
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
class DirectSharingOAuth2Tests(DirectSharingMixin, DirectSharingTestsMixin,
                               TestCase):
    """
    Tests for private sharing OAuth2 projects.
    """

    @classmethod
    def setUpClass(cls):
        super(DirectSharingOAuth2Tests, cls).setUpClass()

        cls.authorize_url = ('/direct-sharing/projects/oauth2/authorize/'
                             '?client_id=test-key&response_type=code')

        user1 = get_or_create_user('beau')
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
            '/account/login/oauth2/?connection=abc&next={}'.format(
                quote(self.authorize_url, safe='')))

    def test_authorize_if_logged_in(self):
        login = self.client.login(username='beau', password='test')
        self.assertTrue(login)

        self.update_member(joined=False, authorized=False)

        response = self.client.get(self.authorize_url)

        self.assertEqual(response.status_code, 200)

    def test_authorize_if_already_authorized(self):
        login = self.client.login(username='beau', password='test')
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
        self.assertTrue(json['username'] == 'beau')
        self.assertTrue(json['message_permission'] is True)

        self.assertTrue(len(json['sources_shared']) == 4)

        self.assertTrue('american_gut' in json['sources_shared'])
        self.assertTrue('ancestry_dna' in json['sources_shared'])
        self.assertTrue('data_selfie' in json['sources_shared'])
        self.assertTrue('twenty_three_and_me' in json['sources_shared'])
        self.assertFalse('direct-sharing-1' in json['sources_shared'])

        datafile_sources = [x['source'] for x in json['data']]
        self.assertIn('twenty_three_and_me', datafile_sources)

        # Project sees its own data.
        self.assertIn('direct-sharing-1', datafile_sources)

        # Unauthorized data not available.
        self.assertNotIn('direct-sharing-2', datafile_sources)

    def test_oauth2_authorize(self):
        login = self.client.login(username='beau', password='test')
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

    def test_member_access_token(self):
        member = self.update_member(joined=True, authorized=True)

        response = self.client.post(
            '/api/direct-sharing/project/files/upload/?access_token={}'.format(
                self.access_token),
            data={
                'project_member_id': member.project_member_id,
                'metadata': ('{"description": "Test description...", '
                             '"tags": ["tag 1", "tag 2", "tag 3"]}'),
                'data_file': StringIO('just testing...'),
            })

        response_json = response.json()

        self.assertIn('id', response_json)
        self.assertEqual(response.status_code, 201)
        self.assertNotIn('errors', response_json)

        data_file = ProjectDataFile.objects.get(
            id=response_json['id'],
            direct_sharing_project=self.member1_project,
            user=self.member1.user)

        self.assertEqual(data_file.metadata['description'],
                         'Test description...')

        self.assertEqual(data_file.metadata['tags'],
                         ['tag 1', 'tag 2', 'tag 3'])

        self.assertEqual(data_file.file.readlines(), ['just testing...'])

    def test_message_member(self):
        member = self.update_member(joined=True, authorized=True)

        response = self.client.post(
            '/api/direct-sharing/project/message/?access_token=def456',
            data={
                'project_member_ids': [member.project_member_id],
                'subject': 'Sending a good test email',
                'message': 'The content of this email\nis a test.\n'
            })

        response_json = response.json()
        self.assertEqual(response_json, 'success')


    def test_message_deauthorized_member(self):
        member = self.update_member(joined=False, authorized=False,
                                    revoked=True)

        response = self.client.post(
            '/api/direct-sharing/project/message/?access_token=def456',
            data={
                'project_member_ids': [member.project_member_id],
                'subject': 'Sending a bad test email',
                'message': 'The content of this email\nis a test.\n'
            })

        response_json = response.json()
        self.assertIn('errors', response_json)
        self.assertIn('project_member_ids', response_json['errors'])
        self.assertIn('Invalid project member ID',
                      response_json['errors']['project_member_ids'][0])


@override_settings(SSLIFY_DISABLE=True)
class DirectSharingOAuth2Tests2(DirectSharingMixin, TestCase):
    """
    Another OAuth2 project to test alternate setup situations.

    - master token expired
    - all_sources_access true

    Because the master token is expired, skip DirectSharingTestsMixin as these
    are expected to fail.
    """

    @classmethod
    def setUpClass(cls):
        super(DirectSharingOAuth2Tests2, cls).setUpClass()

        cls.authorize_url = ('/direct-sharing/projects/oauth2/authorize/'
                             '?client_id=test-key-2&response_type=code')

        user1 = get_or_create_user('beau')
        cls.member1, _ = Member.objects.get_or_create(user=user1)
        cls.member1_project = OAuth2DataRequestProject.objects.get(
            slug='abc3')
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

    def test_exchange_member_all_sources(self):
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
        self.assertTrue(json['username'] == 'beau')
        self.assertTrue(json['message_permission'] is True)

        self.assertEqual(len(json['sources_shared']), 0)

        datafile_sources = [x['source'] for x in json['data']]
        self.assertIn('direct-sharing-1', datafile_sources)

    def test_message_expired_master_token(self):
        member = self.update_member(joined=True, authorized=True)

        response = self.client.post(
            '/api/direct-sharing/project/message/?access_token=ghi789',
            data={
                'project_member_ids': [member.project_member_id],
                'subject': 'Sending a good test email',
                'message': 'The content of this email\nis a test.\n'
            })

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()['detail'], 'Expired token.')


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

    @unittest.skipIf(settings.NOBROWSER, "skipping browser tests")
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

    @unittest.skipIf(settings.NOBROWSER, "skipping browser tests")
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
            os.path.abspath('static/images/open_humans_logo_only.png'))

        driver.findElement(By.id("id_request_sources_access_1")).sendKeys(Keys.PAGE_DOWN);
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
            'https://beaugunderson.com/?id=PROJECT_MEMBER_ID')

        driver.find_element_by_id('create-project').click()

        self.assertEqual('Test Study', driver.find_element_by_xpath(
            "//table[@id='on-site-projects']/tbody/tr[1]/td").text)

    @unittest.skipIf(settings.NOBROWSER, "skipping browser tests")
    def test_returned_data_description_activity(self):
        driver = self.driver

        driver.get(self.live_server_url + '/')

        prefix = '//div[@id="activity-direct-sharing-1"]'

        leader = driver.find_element_by_xpath(
            '{}//div[@class="leader"]'.format(prefix)).text
        self.assertIn('abc', leader)
        organization = driver.find_element_by_xpath(
            '{}//div[@class="leader"]'.format(prefix)).text
        self.assertIn('abc', organization)
        description = driver.find_element_by_xpath(
            '{}//p[@class="activity-description"]'.format(prefix)).text
        self.assertIn('abc', description)

        prefix = '//div[@id="activity-direct-sharing-2"]'

        leader = driver.find_element_by_xpath(
            '{}//div[@class="leader"]'.format(prefix)).text
        self.assertIn('xyz', leader)
        organization = driver.find_element_by_xpath(
            '{}//div[@class="leader"]'.format(prefix)).text
        self.assertIn('abcxyz', organization)
        description = driver.find_element_by_xpath(
            '{}//p[@class="activity-description"]'.format(prefix)).text
        self.assertIn('def', description)
