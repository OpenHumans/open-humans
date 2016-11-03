from django.test import TestCase
from oauth2_provider.models import AccessToken

from common.api_testing import APITestCase


class UserDataTests(APITestCase):
    """
    Test the GoViral API URLs.
    """

    base_url = '/go-viral'


class StudyTests(TestCase):
    """
    Test the study URLs.
    """

    fixtures = ['open_humans/fixtures/test-data.json']

    def test_connection_return(self):
        return_url = '/study/go_viral/return/'

        login = self.client.login(username='beau', password='test')
        self.assertEqual(login, True)

        response = self.client.get(return_url)
        self.assertEqual(response.status_code, 200)

        response = self.client.get(return_url + '?origin=open-humans')
        self.assertEqual(response.status_code, 302)

        response = self.client.get(return_url + '?origin=external')
        self.assertEqual(response.status_code, 200)
