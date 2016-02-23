from django.core.urlresolvers import reverse_lazy
from django.views.generic.edit import CreateView

from common.mixins import PrivateMixin

from .models import OAuth2DataRequestActivity  # , OnSiteDataRequestActivity


class CreateOAuth2DataRequestActivityView(PrivateMixin, CreateView):
    """
    Create an OAuth2DataRequestActivity.
    """
    template_name = 'private_sharing/create-oauth2.html'
    model = OAuth2DataRequestActivity

    fields = ('is_study', 'name', 'leader', 'organization',
              'contact_email', 'info_url', 'short_description',
              'long_description', 'active', 'request_sources_access',
              'request_message_permission', 'request_username_access',
              'enrollment_text', 'redirect_url')

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
