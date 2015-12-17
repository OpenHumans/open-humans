from django.apps import AppConfig


class GoViralConfig(AppConfig):
    """
    Configure the GoViral study application.

    Note: The verbose_name matches the 'name' assigned for this study's API
    client. This is the 'name' field for its corresponding oauth2_provider
    Application, and was set by the setup_api management command in
    open_humans/management/commands/setup_api.py
    """
    name = 'studies.go_viral'
    verbose_name = 'GoViral'

    data_description = {
        'name': 'Sickness reports and viral profiling data',
        'description':
            ('Sickness reports contain demographic and illness survey '
             'data from GoViral. They may contain sensitive information, '
             'including your exact birthdate and ZIP code. Viral '
             'profiling data contains raw data results from viral '
             'testing, performed on samples you contributed to GoViral.'),
    }

    def ready(self):
        # Make sure our signal handlers get hooked up

        # pylint: disable=unused-variable
        import studies.go_viral.signals  # noqa
