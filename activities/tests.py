from common.testing import SmokeTestCase


class SmokeTests(SmokeTestCase):
    """
    Simple tests for all of the activity URLs in the site.
    """

    authenticated_urls = [
        '/activity/withings/finalize-import/',
    ]

    post_only_urls = [
        '/activity/withings/disconnect/',
    ]
