from social.backends.oauth import BaseOAuth2


class TwentyThreeAndMeOAuth2(BaseOAuth2):
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
