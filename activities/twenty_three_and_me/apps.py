from common.app_configs import BaseConnectionAppConfig


class TwentyThreeAndMeConfig(BaseConnectionAppConfig):
    """
    Configure the 23andme activity application.
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
