from django.test import TestCase
from oauth2_provider.models import AccessToken

from common.api_testing import APITestCase


class UserDataTests(APITestCase):
    """
    Test the PGP API URLs.
    """

    base_url = '/pgp'

    def test_get_user_data(self):
        """
        Ensure we can get a UserData object with credentials.
        """
        access_token = AccessToken.objects.filter(
            user__username='beau',
            application__name='Harvard Personal Genome Project')[0]

        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + access_token.token)

        self.verify_request('/user-data/')
        self.verify_request('/huids/')
        self.verify_request('/huids/', method='post', status=201,
                            body={'value': 'hu000005'})
        self.verify_request('/huids/hu000005/')

    def test_get_user_data_no_credentials(self):
        """
        Ensure we can't get a UserData object with no credentials.
        """
        self.client.credentials()

        self.verify_request('/user-data/', status=401)
        self.verify_request('/huids/', status=401)


class StudyTests(TestCase):
    """
    Tests for study URLs.
    """

    fixtures = ['open_humans/fixtures/test-data.json']

    def test_connection_return(self):
        return_url = '/study/pgp/return/'

        login = self.client.login(username='beau', password='test')
        self.assertEqual(login, True)

        response = self.client.get(return_url)
        self.assertEqual(response.status_code, 200)

        response = self.client.get(return_url + '?origin=open-humans')
        self.assertEqual(response.status_code, 302)

        response = self.client.get(return_url + '?origin=external')
        self.assertEqual(response.status_code, 200)
