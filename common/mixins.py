from django.core.urlresolvers import reverse_lazy
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


class LargePanelMixin(object):
    """
    Add panel width and offset to this view's context.
    """
    def get_context_data(self, **kwargs):
        context = super(LargePanelMixin, self).get_context_data(**kwargs)

        context.update({
            'panel_width': 8,
            'panel_offset': 2,
        })

        return context


class UserSocialAuthUserData(object):
    """
    Implements methods for UserData models that use Python Social Auth to
    connect users.
    """

    # TODO: when this is no longer used as a model mixin:
    # 1. remove hasattr check
    # 2. remove default None parameter
    def __init__(self, provider=None):
        if not hasattr(self, 'provider'):
            self.provider = provider

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
        Get the access token from the most recent RunKeeeper association.
        """
        user_social_auth = (self.user.social_auth.filter(
            provider=self.provider).order_by('-id')[0])

        return user_social_auth.extra_data['access_token']
