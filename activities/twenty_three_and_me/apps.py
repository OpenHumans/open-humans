from django.apps import AppConfig


class TwentyThreeAndMeConfig(AppConfig):
    """
    Configure the 23andme activity application.

    Note: The verbose_name matches the name of the 'provider' defined for this
    activity's authentication backend, as used by python-social-auth. For this
    activity, the backend is defined in common/oauth_backends.py
    """
    name = 'activities.twenty_three_and_me'
    verbose_name = '23andMe'
