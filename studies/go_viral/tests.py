from oauth2_provider.models import AccessToken

from common.testing import APITestCase


class UserDataTests(APITestCase):
    """
    Test the GoViral API URLs.
    """

    base_url = '/go-viral'

    def test_get_user_data(self):
        """
        Ensure we can get a UserData object with credentials.
        """
        access_token = AccessToken.objects.get(pk=1)

        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + access_token.token)

        self.verify_request('/user-data/')
        self.verify_request('/ids/')
        self.verify_request('/ids/1/')
        self.verify_request('/ids/5/')
        self.verify_request('/ids/5/', status=204, method='delete')
        self.verify_request('/ids/5/', status=404)
        self.verify_request('/ids/', method='post', status=201,
                            data={'value': '5'})
        self.verify_request('/ids/5/')

    def test_get_user_data_no_credentials(self):
        """
        Ensure we can't get a UserData object with no credentials.
        """
        self.client.credentials()

        self.verify_request('/user-data/', status=401)
        self.verify_request('/ids/', status=401)
        self.verify_request('/ids/1/', status=401)
        self.verify_request('/ids/1/', status=401, method='delete')
        self.verify_request('/ids/5/', status=401)
