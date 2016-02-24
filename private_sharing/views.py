from django.core.urlresolvers import reverse_lazy
from django.views.generic.edit import CreateView

from common.mixins import PrivateMixin

from .forms import OAuth2DataRequestActivityForm, OnSiteDataRequestActivityForm
from .models import OAuth2DataRequestActivity, OnSiteDataRequestActivity


class CreateDataRequestActivityView(PrivateMixin, CreateView):
    """
    Base view for creating an data request activities.
    """

    success_url = reverse_lazy('my-member-settings')

    def form_valid(self, form):
        """
        If the form is valid, redirect to the supplied URL.
        """
        form.instance.coordinator = self.request.user.member

        return super(CreateDataRequestActivityView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(CreateDataRequestActivityView, self).get_context_data(
            **kwargs)

        context.update({
            'panel_width': 8,
            'panel_offset': 2,
        })

        return context


class CreateOAuth2DataRequestActivityView(CreateDataRequestActivityView):
    """
    Create an OAuth2DataRequestActivity.
    """

    template_name = 'private_sharing/create-activity.html'
    model = OAuth2DataRequestActivity
    form_class = OAuth2DataRequestActivityForm


class CreateOnSiteDataRequestActivityView(CreateDataRequestActivityView):
    """
    Create an OnSiteDataRequestActivity.
    """

    template_name = 'private_sharing/create-activity.html'
    model = OnSiteDataRequestActivity
    form_class = OnSiteDataRequestActivityForm
