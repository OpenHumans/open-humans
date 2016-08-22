class UserSocialAuthUserData(object):
    """
    Implements methods for UserData models that use Python Social Auth to
    connect users.
    """

    def __init__(self, provider, user):
        self.provider = provider
        self.user = user

    def __unicode__(self):
        return '<UserSocialAuthUserData:{}>'.format(self.provider)

    @property
    def is_connected(self):
        # filter in Python to benefit from prefetched data
        return len([s for s in self.user.social_auth.all()
                    if s.provider == self.provider]) > 0

    def to_list(self):
        if self.user:
            return [self]

        # XXX: this import is located here because if it's at the top of the
        # file and we use this class from a management command we get a
        # "AppRegistryNotReady" exception.
        from social.apps.django_app.default.models import UserSocialAuth

        return [UserSocialAuthUserData(self.provider, auth.user)
                for auth
                in UserSocialAuth.objects.filter(provider=self.provider)]

    def disconnect(self):
        self.user.social_auth.filter(provider=self.provider).delete()

    # access tokens are handled in task_params_for_source
    @staticmethod
    def get_retrieval_params():
        return {}
