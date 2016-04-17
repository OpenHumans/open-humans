from activities.app_configs import UploadAppConfig


class MPowerConfig(UploadAppConfig):
    """
    Configure the mPower activity application.
    """

    name = __package__
    verbose_name = 'mPower'

    url_slug = 'mpower'

    organization_description = """The mPower study uses an iPhone app to
    investigate, track, and understand the symptoms of Parkinson's disease.
    """

    data_description = {
        'name': 'Survey, task, and sensor data',
        'description': (
            'Health history and other mPower survey data. Daily walking '
            'distance from HealthKit. Records and sensor data from voice, '
            'motion, and memory tasks.'),
    }
