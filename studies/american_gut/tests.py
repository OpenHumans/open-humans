from django.test import SimpleTestCase
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
        access_token = AccessToken.objects.get(pk=1)

        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + access_token.token)

        self.verify_request('/user-data/')
        self.verify_request('/barcodes/')
        self.verify_request('/barcodes/111111/')
        self.verify_request('/barcodes/555555/')
        self.verify_request('/barcodes/555555/', status=204, method='delete')
        self.verify_request('/barcodes/555555/', status=404)
        self.verify_request('/barcodes/', method='post', status=201,
                            body={'value': '555555'})
        self.verify_request('/barcodes/555555/')

    def test_get_user_data_no_credentials(self):
        """
        Ensure we can't get a UserData object with no credentials.
        """
        self.client.credentials()

        self.verify_request('/user-data/', status=401)
        self.verify_request('/barcodes/', status=401)
        self.verify_request('/barcodes/111111/', status=401)
        self.verify_request('/barcodes/111111/', status=401, method='delete')
        self.verify_request('/barcodes/555555/', status=401)


class StudyTests(SimpleTestCase):
    """
    Test the study URLs.
    """

    def test_connection_return(self):
        return_url = '/study/american_gut/return/'

        response = self.client.get(return_url)
        self.assertEqual(response.status_code, 200)

        response = self.client.get(return_url + '?origin=open-humans')
        self.assertEqual(response.status_code, 302)

        response = self.client.get(return_url + '?origin=external')
        self.assertEqual(response.status_code, 200)
