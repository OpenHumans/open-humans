from django.test import TestCase
from oauth2_provider.models import AccessToken

from common.testing import APITestCase


class UserDataTests(APITestCase):
    """
    Test the American Gut API URLs.
    """

    base_url = '/american-gut'

    def test_get_user_data(self):
        """
        Ensure we can get a UserData object with credentials.
        """
        access_token = AccessToken.objects.filter(
            user__username='beau',
            application__name='American Gut')[0]

        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + access_token.token)

        response = self.verify_request('/user-data/')

        user_data_id = response['id']

        self.verify_request('/user-data/', method='patch', body={
            'data': {
                'surveyIds': ['abc', 'def']
            }
        })

        self.verify_request('/user-data/', method='get', body={
            u'data': {
                u'surveyIds': [u'abc', u'def']
            },
            u'id': user_data_id
        })

    def test_get_user_data_no_credentials(self):
        """
        Ensure we can't get a UserData object with no credentials.
        """
        self.client.credentials()

        self.verify_request('/user-data/', status=401)


class StudyTests(TestCase):
    """
    Test the study URLs.
    """

    fixtures = ['open_humans/fixtures/test-data.json']

    def test_connection_return(self):
        return_url = '/study/american_gut/return/'

        login = self.client.login(username='beau', password='test')
        self.assertEqual(login, True)

        response = self.client.get(return_url)
        self.assertEqual(response.status_code, 200)

        response = self.client.get(return_url + '?origin=open-humans')
        self.assertEqual(response.status_code, 302)

        response = self.client.get(return_url + '?origin=external')
        self.assertEqual(response.status_code, 200)
