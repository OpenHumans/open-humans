from django.apps import AppConfig


class RunKeeperConfig(AppConfig):
    """
    Configure the RunKeeper activity application.
    """
    name = 'activities.runkeeper'
    verbose_name = 'RunKeeper'

    # TODO: DRY this URL
    connection_url = '/auth/login/runkeeper/'
