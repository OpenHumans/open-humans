from django.core.urlresolvers import reverse_lazy
from django.views.generic import CreateView, TemplateView

from common.mixins import LargePanelMixin, PrivateMixin
from common.utils import get_source_labels_and_configs

from .forms import OAuth2DataRequestActivityForm, OnSiteDataRequestActivityForm
from .models import OAuth2DataRequestActivity, OnSiteDataRequestActivity


class CreateDataRequestActivityView(PrivateMixin, LargePanelMixin, CreateView):
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


class OverviewView(TemplateView):
    """
    Add current sources to template context.
    """
    template_name = 'private_sharing/overview.html'

    def get_context_data(self, **kwargs):
        print "IN GET CONTEXT DATA"
        context = super(OverviewView, self).get_context_data(**kwargs)
        source_labels_and_configs = get_source_labels_and_configs()
        print source_labels_and_configs
        context.update({
            'sources': get_source_labels_and_configs(),
        })
        return context
