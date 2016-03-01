from django.apps import AppConfig


class BaseConnectionAppConfig(AppConfig):
    """
    A base AppConfig that contains defaults for studies and activities.
    """

    data_description = {
        'name': None,
        'description': None,
    }

    # Can the user disconnect the study or activity?
    disconnectable = True

    # Should files from the study or activity be managed individually?
    individual_deletion = False

    # In-development studies and activities should present themselves as such
    # to the user and not start data retrieval
    in_development = False

    def ready(self):
        """
        Try importing 'signals' relative to the subclassing module. This allows
        our signals to get hooked up when Django starts up.
        """
        super(BaseConnectionAppConfig, self).ready()

        try:
            __import__('{}.signals'.format(self.module.__name__))
        except ImportError:
            # print 'failed to import signals from {}'.format(
            #     self.module.__name__)

            pass
