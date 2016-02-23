from django.core.urlresolvers import reverse_lazy
from django.views.generic.edit import CreateView

from common.mixins import PrivateMixin

from .forms import OAuth2DataRequestActivityForm
from .models import OAuth2DataRequestActivity  # , OnSiteDataRequestActivity


class CreateOAuth2DataRequestActivityView(PrivateMixin, CreateView):
    """
    Create an OAuth2DataRequestActivity.
    """
    template_name = 'private_sharing/create-oauth2.html'
    model = OAuth2DataRequestActivity
    form_class = OAuth2DataRequestActivityForm
    success_url = reverse_lazy('my-member-settings')

    def form_valid(self, form):
        """
        If the form is valid, redirect to the supplied URL.
        """
        form.instance.coordinator = self.request.user.member

        return super(CreateOAuth2DataRequestActivityView,
                     self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(CreateOAuth2DataRequestActivityView,
                        self).get_context_data(**kwargs)

        context.update({
            'panel_width': 8,
            'panel_offset': 2,
        })

        return context
