from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
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
    Override handle_no_permission() to store redirect and add message.
    """
    login_message = 'Please log in or sign up to continue.'

    def get_login_message(self):
        """
        Return message to be set by Django messages. Override to customize.
        """
        return self.login_message

    def handle_no_permission(self):
        """
        Store redirect in session for login/signup and add message.
        """
        if self.raise_exception or self.request.user.is_authenticated:
            raise PermissionDenied(self.get_permission_denied_message())
        self.request.session['next_url'] = self.request.get_full_path()

        message = self.get_login_message()
        messages.add_message(self.request, messages.WARNING, message)

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
