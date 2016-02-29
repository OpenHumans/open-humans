from common.app_configs import BaseConnectionAppConfig


class TwentyThreeAndMeConfig(BaseConnectionAppConfig):
    """
    Configure the 23andme activity application.
    """

    name = __package__
    verbose_name = '23andMe'

    connection_template = 'partials/upload-activity.html'

    data_description = {
        'name': 'Genotyping data',
        'description': (
            'Genetic data from roughly one million locations in your '
            'genome. This can reveal information about health, traits, '
            "ancestry, and who you're related to."),
    }
