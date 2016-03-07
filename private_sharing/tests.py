from common.testing import SmokeTestCase


class SmokeTests(SmokeTestCase):
    """
    A simple GET test for all of the simple URLs in the site.
    """

    authenticated_urls = [
        '/private-sharing/projects/manage/',
        '/private-sharing/projects/oauth2/create/',
        '/private-sharing/projects/oauth2/update/1/',
        '/private-sharing/projects/oauth2/1/',
        '/private-sharing/projects/on-site/create/',
        '/private-sharing/projects/on-site/update/2/',
        '/private-sharing/projects/on-site/2/',
    ]

    authenticated_or_anonymous_urls = [
        '/private-sharing/overview/',
    ]

    fixtures = SmokeTestCase.fixtures + [
        'private_sharing/fixtures/test-data.json',
    ]
