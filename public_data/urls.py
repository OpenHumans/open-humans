from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.views.generic import TemplateView

from .views import ConsentView, QuizView, ToggleSharingView, WithdrawView


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
        login_required(ConsentView.as_view()),
        name='enroll-consent'),
    url(r'^enroll-3-quiz',
        login_required(QuizView.as_view()),
        name='enroll-quiz'),
    url(r'^enroll-4-signature',
        require_POST(login_required(ConsentView.as_view())),
        name='enroll-signature'),

    # Withdraw from the public data study
    url(r'^withdraw',
        login_required(WithdrawView.as_view()),
        name='withdraw'),

    # Data management.
    url(r'^toggle-sharing/', ToggleSharingView.as_view(),
        name='toggle-sharing'),
)
