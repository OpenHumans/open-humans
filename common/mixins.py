from django.views.decorators.cache import never_cache

from .decorators import participant_required


class PrivateMixin(object):
    """
    Require participant status and never cache this view.
    """
    @classmethod
    def as_view(cls, **initkwargs):
        view = super(PrivateMixin, cls).as_view(**initkwargs)

        view = participant_required(view)
        view = never_cache(view)

        return view


class NeverCacheMixin(object):
    """
    Never cache this view.
    """
    @classmethod
    def as_view(cls, **initkwargs):
        view = super(NeverCacheMixin, cls).as_view(**initkwargs)

        view = never_cache(view)

        return view


class UserSocialAuthUserData(object):
    """
    Implements methods for UserData models that use Python Social Auth to
    connect users.
    """

    provider = None

    @property
    def is_connected(self):
        # filter in Python to benefit from the prefetch data
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
        Get the access token from the most recent RunKeeeper association.
        """
        user_social_auth = (self.user.social_auth.filter(
            provider=self.provider).order_by('-id')[0])

        return user_social_auth.extra_data['access_token']
