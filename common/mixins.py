from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache


class PrivateMixin(object):
    """
    Require login and never cache this view.
    """
    @classmethod
    def as_view(cls, **initkwargs):
        view = super(PrivateMixin, cls).as_view(**initkwargs)

        view = login_required(view)
        view = never_cache(view)

        return view
