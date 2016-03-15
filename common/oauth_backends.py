import base64

from social.backends.oauth import BaseOAuth1, BaseOAuth2


class WithingsOAuth1(BaseOAuth1):  # pylint: disable=abstract-method
    """
    Withings OAuth1 authentication backend
    """

    name = 'withings'

    ID_KEY = 'userid'

    AUTHORIZATION_URL = 'https://oauth.withings.com/account/authorize'
    REQUEST_TOKEN_URL = 'https://oauth.withings.com/account/request_token'
    ACCESS_TOKEN_URL = 'https://oauth.withings.com/account/access_token'

    EXTRA_DATA = [('userid', 'id')]

    def get_user_id(self, details, response):
        return response['access_token'][self.ID_KEY]

    def get_user_details(self, response):
        """
        Return user details from Withings account
        """
        return {
            'userid': response['access_token'][self.ID_KEY],
            'email': ''  # not provided by Withings
        }


# From this pull request:
# https://github.com/omab/python-social-auth/pull/743/files#diff-82b8b42cc8d4096a65dd44643ee1b9b4
class FitbitOAuth2(BaseOAuth2):  # pylint: disable=abstract-method
    """
    Fitbit OAuth2 authentication backend
    """

    name = 'fitbit'

    ID_KEY = 'encodedId'

    AUTHORIZATION_URL = 'https://www.fitbit.com/oauth2/authorize'
    ACCESS_TOKEN_URL = 'https://api.fitbit.com/oauth2/token'
    REFRESH_TOKEN_URL = 'https://api.fitbit.com/oauth2/token'

    ACCESS_TOKEN_METHOD = 'POST'
    DEFAULT_SCOPE = ['profile']
    REDIRECT_STATE = False

    EXTRA_DATA = [('expires_in', 'expires'),
                  ('refresh_token', 'refresh_token', True),
                  ('encodedId', 'id'),
                  ('displayName', 'username')]

    def get_user_details(self, response):
        """
        Return user details from Fitbit account
        """
        return {
            'username': response.get('displayName'),
            'email': ''
        }

    def user_data(self, access_token, *args, **kwargs):
        """
        Load user data from service
        """
        auth_header = {'Authorization': 'Bearer %s' % access_token}

        return self.get_json(
            'https://api.fitbit.com/1/user/-/profile.json',
            headers=auth_header)['user']

    def auth_headers(self):
        return {
            'Authorization': 'Basic {0}'.format(base64.urlsafe_b64encode(
                ('{0}:{1}'.format(*self.get_key_and_secret()).encode())))
        }
