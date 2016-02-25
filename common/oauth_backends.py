import base64

from social.backends.oauth import BaseOAuth2


class TwentyThreeAndMeOAuth2(BaseOAuth2):  # pylint: disable=abstract-method
    """
    23andMe OAuth2 authentication backend
    """
    name = '23andme'

    ID_KEY = 'id'

    AUTHORIZATION_URL = 'https://api.23andme.com/authorize'
    ACCESS_TOKEN_URL = 'https://api.23andme.com/token'

    ACCESS_TOKEN_METHOD = 'POST'
    REFRESH_TOKEN_METHOD = 'POST'

    SCOPE_SEPARATOR = ' '

    REDIRECT_STATE = False
    STATE_PARAMETER = False

    EXTRA_DATA = [
        ('access_token', 'access_token'),
        ('refresh_token', 'refresh_token'),
        ('scope', 'scope'),
    ]

    def get_user_id(self, details, response):
        """
        Return a unique ID for the current user, by default from server
        response.
        """
        return response.get(self.ID_KEY)

    def get_user_details(self, response):
        """
        In 23andMe, basic scope returns none of these fields.
        """
        return {
            'username': '',
            'email': '',
            'fullname': '',
            'first_name': '',
            'last_name': ''
        }

    # pylint: disable=unused-argument
    def user_data_basic(self, access_token, *args, **kwargs):
        """
        Load basic user data from 23andme

        Scope required: basic

        This retrieves the following account data:
        'id'             id for this account
        'profiles'       list of profiles in the account

        Each profile has:
            'id'         id for this profile
            'genotyped'  whether a profile has been genotyped
            'services'   list of services that profile has access to
        """
        assert 'basic' in self.get_scope(), "'basic' scope required"

        params = {'services': 'true'}
        headers = {'Authorization': 'Bearer %s' % access_token}

        return self.get_json('https://api.23andme.com/1/user/',
                             params=params, headers=headers)

    def user_data(self, access_token, *args, **kwargs):
        return self.user_data_basic(access_token, *args, **kwargs)

    def auth_complete_params(self, *args, **kwargs):
        params = super(TwentyThreeAndMeOAuth2,
                       self).auth_complete_params(*args, **kwargs)
        params.update(self.get_scope_argument())

        return params


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
