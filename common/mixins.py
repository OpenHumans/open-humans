from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.views.decorators.cache import never_cache


class NeverCacheMixin(object):
    """
    Never cache this view.
    """

    @classmethod
    def as_view(cls, **initkwargs):
        view = super().as_view(**initkwargs)
        view = never_cache(view)
        return view


class PrivateMixin(LoginRequiredMixin, NeverCacheMixin):
    """
    Overriding handle_no_permission() to change redirect behavior

    """

    def handle_no_permission(self):
        """
        We want to set the redirect in the session rather than redirect using a
        next= parameter.
        https://docs.djangoproject.com/en/2.1/topics/auth/default/#django.contrib.auth.mixins.AccessMixin.handle_no_permission
        """
        if self.raise_exception or self.request.user.is_authenticated:
            raise PermissionDenied(self.get_permission_denied_message())
        self.request.session['next_url'] = self.request.get_full_path()
        return redirect(self.get_login_url())


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
