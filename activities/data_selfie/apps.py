from common.app_configs import BaseConnectionAppConfig


class DataSelfieConfig(BaseConnectionAppConfig):
    """
    Configure the data selfie activity application.

    Note: The verbose_name matches the name of the 'provider' defined for this
    activity's authentication backend, as used by python-social-auth. For this
    activity, the backend is defined in common/oauth_backends.py
    """
    name = __package__
    verbose_name = 'Data selfie'

    disconnectable = False
    individual_deletion = True

    data_description = {
        'name': '',
        'description': '',
    }
