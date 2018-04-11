from common.testing import SmokeTestCase


class SmokeTests(SmokeTestCase):
    """
    Simple tests for all of the activity URLs in the site.
    """

    authenticated_urls = [
        '/activity/fitbit/finalize-import/',
        '/activity/jawbone/finalize-import/',
        '/activity/moves/finalize-import/',
        '/activity/runkeeper/finalize-import/',
        '/activity/withings/finalize-import/',
    ]

    post_only_urls = [
        # needs to happen before /disconnect/ or the /disconnect test fails
        '/activity/runkeeper/request-data-retrieval/',

        '/activity/fitbit/disconnect/',
        '/activity/jawbone/disconnect/',
        '/activity/moves/disconnect/',
        '/activity/runkeeper/disconnect/',
        '/activity/withings/disconnect/',
    ]
