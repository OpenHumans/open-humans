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
