import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from oauth2_provider.models import Application

API_USERNAME = 'api-administrator'

UserModel = get_user_model()


def get_api_user():
    """
    Get or create the API administrator user.
    """
    try:
        api_administrator = UserModel.objects.get(username=API_USERNAME)
    except UserModel.DoesNotExist:
        api_administrator = UserModel()

    api_administrator.username = API_USERNAME
    api_administrator.save()

    return api_administrator


def get_or_create_app(name, redirect_uri, user, client_id=None,
                      client_secret=None):
    """
    Get or creates an OAuth2 application.
    """
    try:
        application = Application.objects.get(name=name)
    except Application.DoesNotExist:
        application = Application()

    application.user = user

    if client_id and client_secret:
        application.client_id = client_id
        application.client_secret = client_secret

    application.name = name
    application.authorization_grant_type = \
        Application.GRANT_AUTHORIZATION_CODE
    application.client_type = Application.CLIENT_CONFIDENTIAL
    application.redirect_uris = redirect_uri

    application.save()

    return application


class Command(BaseCommand):
    """
    Generate API client IDs and secrets for our partner applications.
    """

    help = 'Sets up the partner API keys'

    def handle(self, *args, **options):
        partners = [{
            'name': 'GoViral',
            'redirect_uri': ('https://www.goviralstudy.com/'
                             'auth/open-humans/callback'),
            'env_key': 'GO_VIRAL',
        }, {
            'name': 'American Gut',
            'redirect_uri': ('https://www.microbio.me/AmericanGut/'
                             'authed/connect/open-humans/'),
            'env_key': 'AMERICAN_GUT',
        }, {
            'name': 'Harvard Personal Genome Project',
            'redirect_uri': ('https://my.pgp-hms.org/'
                             'auth/open-humans/callback'),
            'env_key': 'PGP',
        }, {
            'name': 'Wildlife of Our Homes',
            'redirect_uri': ('http://wildlife.lvh.me:8007/'
                             'open_humans_complete/'),
            'env_key': 'WILDLIFE',
        }]

        api_user = get_api_user()

        for partner in partners:
            self.stdout.write('')
            self.stdout.write(partner['name'])
            self.stdout.write('')

            client_id = os.getenv(partner['env_key'] + '_CLIENT_ID')
            client_secret = os.getenv(partner['env_key'] + '_CLIENT_SECRET')

            application = get_or_create_app(
                name=partner['name'],
                redirect_uri=partner['redirect_uri'],
                client_id=client_id,
                client_secret=client_secret,
                user=api_user)

            self.stdout.write(('OPEN_HUMANS_CLIENT_ID="{}"'
                               .format(application.client_id)))
            self.stdout.write(('OPEN_HUMANS_CLIENT_SECRET="{}"'
                               .format(application.client_secret)))
            self.stdout.write(('OPEN_HUMANS_CALLBACK_URL="{}"'
                               .format(application.redirect_uris)))
