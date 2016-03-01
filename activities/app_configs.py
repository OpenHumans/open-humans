from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse_lazy

from activities.user_data import UserSocialAuthUserData
from common.app_configs import BaseConnectionAppConfig


class UserSocialAuthAppConfig(BaseConnectionAppConfig):
    """
    An AppConfig used for activities that connect via UserSocialAuth.
    """

    def get_user_data(self):
        outer_self = self

        @property
        def get_user_data_inner(self):
            return outer_self.user_data(user=self)

        return get_user_data_inner

    def user_data(self, user=None):
        user_data = UserSocialAuthUserData(provider=self.label, user=user)

        # TODO: remove this duplication
        user_data.text_name = self.verbose_name

        return user_data

    @property
    def connection_url(self):
        return reverse_lazy('social:begin', args=(self.label,))

    @property
    def finalization_url(self):
        return reverse_lazy('activities:{}:finalize-import'.format(self.label))

    connection_template = 'partials/connection-activity.html'

    def ready(self):
        super(UserSocialAuthAppConfig, self).ready()

        UserModel = get_user_model()
        UserModel.add_to_class(self.label, self.get_user_data())
