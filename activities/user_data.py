from django.core.urlresolvers import reverse_lazy


class UserSocialAuthUserData(object):
    """
    Implements methods for UserData models that use Python Social Auth to
    connect users.
    """

    # TODO: this duplicates the AppConfig's verbose_name attribute
    text_name = None

    # TODO: when this is no longer used as a model mixin:
    # 1. remove hasattr check
    # 2. remove default None parameter
    def __init__(self, provider=None, user=None):
        if not hasattr(self, 'provider'):
            self.provider = provider
            self.user = user

    def __unicode__(self):
        return '<UserSocialAuthUserData:{}>'.format(self.provider)

    @property
    def href_connect(self):
        return reverse_lazy('social:begin', args=(self.provider,))

    @property
    def href_next(self):
        return reverse_lazy('activities:{}:finalize-import'
                            .format(self.provider))

    @property
    def retrieval_url(self):
        return reverse_lazy('activities:{}:request-data-retrieval'
                            .format(self.provider))

    @property
    def is_connected(self):
        # filter in Python to benefit from prefetched data
        return len([s for s in self.user.social_auth.all()
                    if s.provider == self.provider]) > 0

    def disconnect(self):
        self.user.social_auth.filter(provider=self.provider).delete()

    def get_retrieval_params(self):
        return {
            'access_token': self.get_access_token(),
        }

    def get_access_token(self):
        """
        Get the access token from the most recent association with this
        provider.
        """
        user_social_auth = (self.user.social_auth.filter(
            provider=self.provider).order_by('-id')[0])

        return user_social_auth.extra_data['access_token']
