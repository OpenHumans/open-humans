from common.app_configs import BaseConnectionAppConfig


class TwentyThreeAndMeConfig(BaseConnectionAppConfig):
    """
    Configure the 23andme activity application.

    Note: The verbose_name matches the name of the 'provider' defined for this
    activity's authentication backend, as used by python-social-auth. For this
    activity, the backend is defined in common/oauth_backends.py
    """
    name = 'activities.twenty_three_and_me'
    verbose_name = '23andMe'

    data_description = {
        'name': 'Genotyping data',
        'description': (
            'Genetic data from roughly one million locations in your '
            'genome. This can reveal information about health, traits, '
            "ancestry, and who you're related to."),
    }
