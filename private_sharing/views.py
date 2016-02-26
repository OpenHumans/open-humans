from django.core.urlresolvers import reverse_lazy
from django.views.generic import (CreateView, DetailView, TemplateView,
                                  UpdateView)

from common.mixins import LargePanelMixin, PrivateMixin
from common.utils import get_source_labels_and_configs

from .forms import OAuth2DataRequestProjectForm, OnSiteDataRequestProjectForm
from .models import OAuth2DataRequestProject, OnSiteDataRequestProject


class UpdateDataRequestProjectView(PrivateMixin, LargePanelMixin, UpdateView):
    """
    Base view for creating an data request activities.
    """

    success_url = reverse_lazy('private-sharing:manage-projects')


class CreateDataRequestProjectView(PrivateMixin, LargePanelMixin, CreateView):
    """
    Base view for creating an data request activities.
    """

    success_url = reverse_lazy('private-sharing:manage-projects')

    def form_valid(self, form):
        """
        If the form is valid, redirect to the supplied URL.
        """
        form.instance.coordinator = self.request.user.member

        return super(CreateDataRequestProjectView, self).form_valid(form)


class CreateOAuth2DataRequestProjectView(CreateDataRequestProjectView):
    """
    Create an OAuth2DataRequestProject.
    """

    template_name = 'private_sharing/create-project.html'
    model = OAuth2DataRequestProject
    form_class = OAuth2DataRequestProjectForm


class CreateOnSiteDataRequestProjectView(CreateDataRequestProjectView):
    """
    Create an OnSiteDataRequestProject.
    """

    template_name = 'private_sharing/create-project.html'
    model = OnSiteDataRequestProject
    form_class = OnSiteDataRequestProjectForm


class UpdateOAuth2DataRequestProjectView(UpdateDataRequestProjectView):
    """
    Update an OAuth2DataRequestProject.
    """

    template_name = 'private_sharing/update-project.html'
    model = OAuth2DataRequestProject
    form_class = OAuth2DataRequestProjectForm


class UpdateOnSiteDataRequestProjectView(UpdateDataRequestProjectView):
    """
    Update an OnSiteDataRequestProject.
    """

    template_name = 'private_sharing/update-project.html'
    model = OnSiteDataRequestProject
    form_class = OnSiteDataRequestProjectForm


class OAuth2DataRequestProjectDetailView(PrivateMixin, DetailView):
    """
    Display an OAuth2DataRequestProject.
    """

    template_name = 'private_sharing/project-detail.html'
    model = OAuth2DataRequestProject


class OnSiteDataRequestProjectDetailView(PrivateMixin, DetailView):
    """
    Display an OnSiteDataRequestProject.
    """

    template_name = 'private_sharing/project-detail.html'
    model = OnSiteDataRequestProject


class ManageDataRequestActivitiesView(PrivateMixin, TemplateView):
    """
    A view for listing all data request activities for the current user.
    """

    template_name = 'private_sharing/manage.html'

    def get_context_data(self, **kwargs):
        context = super(ManageDataRequestActivitiesView, self).get_context_data(
            **kwargs)

        query = {'coordinator__user': self.request.user}

        oauth2 = OAuth2DataRequestProject.objects.filter(**query)
        onsite = OnSiteDataRequestProject.objects.filter(**query)

        context.update({
            'onsite': onsite,
            'oauth2': oauth2,
        })

        return context


class OverviewView(TemplateView):
    """
    Add current sources to template context.
    """

    template_name = 'private_sharing/overview.html'

    def get_context_data(self, **kwargs):
        context = super(OverviewView, self).get_context_data(**kwargs)

        context.update({
            'sources': get_source_labels_and_configs(),
        })

        return context
