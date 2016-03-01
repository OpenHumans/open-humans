from django.contrib import messages as django_messages
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseRedirect
from django.views.generic import View

from common.mixins import PrivateMixin
from common.utils import app_label_to_verbose_name


class DisconnectView(PrivateMixin, View):
    """
    Delete any credentials the user may have.
    """

    source = None

    def post(self, request):
        user_data = getattr(request.user, self.source)
        user_data.disconnect()

        django_messages.success(request, (
            'You have removed your connection to {}.'.format(
                app_label_to_verbose_name(self.source))))

        return HttpResponseRedirect(reverse_lazy('my-member-research-data'))
