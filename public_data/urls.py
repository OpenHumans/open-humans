from django.conf.urls import include, patterns, url
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView


urlpatterns = patterns(
    '',

    url(r'^$',
        TemplateView.as_view(template_name='public_data/home.html'),
        name='home'),
    url(r'^consent/',
        TemplateView.as_view(template_name='public_data/consent.html'),
        name='consent'),
    url(r'^protocol/',
        TemplateView.as_view(template_name='public_data/protocol.html'),
        name='protocol'),

    # Enrollment process pages. User must be logged in to access.
    url(r'^enroll-1-overview',
        login_required(TemplateView.as_view(
            template_name='public_data/overview.html')),
        name='enroll-overview'),
    url(r'^enroll-2-consent',
        login_required(TemplateView.as_view(
            template_name='public_data/consent.html')),
        name='enroll-consent'),

)
