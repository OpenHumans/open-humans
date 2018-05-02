from common.testing import SmokeTestCase


class SmokeTests(SmokeTestCase):
    """
    Simple tests for all of the activity URLs in the site.
    """

    authenticated_urls = [
        '/activity/fitbit/finalize-import/',
        '/activity/withings/finalize-import/',
    ]

    post_only_urls = [
        '/activity/fitbit/disconnect/',
        '/activity/withings/disconnect/',
    ]
