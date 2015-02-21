from django.test.runner import DiscoverRunner


class OpenHumansDiscoverRunner(DiscoverRunner):
    """
    A test runner that silences a warning that occurs during testing against
    sqlite databases.
    """
    def setup_test_environment(self, **kwargs):
        super(OpenHumansDiscoverRunner, self).setup_test_environment(**kwargs)

        import warnings
        import exceptions

        # Filter out the 'naive timezone' warning when using a sqlite database
        warnings.filterwarnings('ignore', category=exceptions.RuntimeWarning,
                                module='django.db.models.fields', lineno=1282)
