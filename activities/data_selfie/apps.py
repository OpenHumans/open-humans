from django.core.urlresolvers import reverse_lazy

from activities.app_configs import UploadAppConfig


class DataSelfieConfig(UploadAppConfig):
    """
    Configure the data selfie activity application.

    Note: The verbose_name matches the name of the 'provider' defined for this
    activity's authentication backend, as used by python-social-auth. For this
    activity, the backend is defined in common/oauth_backends.py
    """
    name = __package__
    verbose_name = 'Data selfie'

    url_slug = 'data-selfie'

    href_connect = reverse_lazy('activities:data-selfie:upload')
    href_add_data = reverse_lazy('activities:data-selfie:upload')

    disconnectable = False
    individual_deletion = True

    connection_template = 'data_selfie/activity.html'

    description = """Do you a have a data type that we don't yet support?
    Upload any files you want to your Data Selfie. Lab results, instrument
    data, and medical imaging are examples of data you might want to share."""

    data_description = {
        'name': 'User-uploaded files',
        'description': 'Diverse data from user-uploaded files.',
    }
