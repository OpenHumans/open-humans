from django.apps import AppConfig


class RunKeeperConfig(AppConfig):
    """
    Configure the RunKeeper activity application.

    Note: The verbose_name matches the name of the 'provider' defined for this
    activity's authentication backend, as used by python-social-auth. For this
    activity, the backend is defined in common/oauth_backends.py
    """
    name = 'activities.runkeeper'
    verbose_name = 'runkeeper'
