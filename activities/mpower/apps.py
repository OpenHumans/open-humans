from django.core.urlresolvers import reverse_lazy

from activities.app_configs import UploadAppConfig


class MPowerConfig(UploadAppConfig):
    """
    Configure the mPower activity application.
    """

    name = __package__
    verbose_name = 'mPower'

    url_slug = 'mpower'

    in_development = True

    description = """The mPower study uses an iPhone app to investigate, track,
    and understand the symptoms of Parkinson's disease."""

    href_connect = reverse_lazy('activities:mpower:upload')
    href_add_data = reverse_lazy('activities:mpower:upload')
    href_learn = 'http://parkinsonmpower.org/'

    retrieval_url = reverse_lazy('activities:mpower:request-data-retrieval')

    leader = 'Stephen Friend'
    organization = 'Sage Bionetworks'

    data_description = {
        'name': 'Survey, task, and sensor data',
        'description': (
            'Health history and other mPower survey data. Daily walking '
            'distance from HealthKit. Records and sensor data from voice, '
            'motion, and memory tasks.'),
    }
