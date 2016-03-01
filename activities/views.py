from django.apps import apps
from django.contrib import messages as django_messages
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseRedirect
from django.views.generic import View


class DisconnectView(View):
    """
    Delete any credentials the user may have.
    """

    source = None

    def post(self, request):
        app = apps.get_app_config(self.source)

        django_messages.success(request, (
            'You have removed your connection to {}.'.format(app.verbose_name)))

        user_data = getattr(request.user, app.name)

        user_data.disconnect()

        return HttpResponseRedirect(reverse_lazy('my-member-research-data'))
