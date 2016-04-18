from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse_lazy

from activities.user_data import UserSocialAuthUserData
from common.app_configs import BaseConnectionAppConfig


class UserSocialAuthAppConfig(BaseConnectionAppConfig):
    """
    An AppConfig used for activities that connect via UserSocialAuth.
    """

    connect_verb = 'Import'

    def get_user_data(self):
        outer_self = self

        @property
        def get_user_data_inner(self):
            return outer_self.user_data(user=self)

        return get_user_data_inner

    @property
    def href_connect(self):
        return reverse_lazy('social:begin', args=(self.label,))

    @property
    def href_next(self):
        return reverse_lazy('activities:{}:finalize-import'.format(self.label))

    @property
    def retrieval_url(self):
        return reverse_lazy('activities:{}:request-data-retrieval'
                            .format(self.label))

    @property
    def connection_url(self):
        return reverse_lazy('social:begin', args=(self.label,))

    @property
    def finalization_url(self):
        return reverse_lazy('activities:{}:finalize-import'.format(self.label))

    def user_data(self, user=None):
        return UserSocialAuthUserData(provider=self.label, user=user)

    connection_template = 'partials/connection-activity.html'

    def ready(self):
        super(UserSocialAuthAppConfig, self).ready()

        UserModel = get_user_model()
        UserModel.add_to_class(self.label, self.get_user_data())


class UploadAppConfig(BaseConnectionAppConfig):
    """
    An AppConfig used for activities that let a user upload files to connect.
    """

    connect_verb = 'Upload'
    connect_complete = 'Uploaded!'

    connection_template = 'partials/upload-activity.html'
