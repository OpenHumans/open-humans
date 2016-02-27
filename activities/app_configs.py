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
            user_data = UserSocialAuthUserData(provider=outer_self.label,
                                               user=self)

            # TODO: remove this duplication
            user_data.text_name = outer_self.verbose_name

            return user_data

        return get_user_data_inner

    @property
    def connection_url(self):
        return reverse_lazy('social:begin', args=(self.label,))

    @property
    def finalization_url(self):
        return reverse_lazy('activities:{}:finalize-import'.format(self.label))

    def ready(self):
        super(UserSocialAuthAppConfig, self).ready()

        UserModel = get_user_model()
        UserModel.add_to_class(self.label, self.get_user_data())
