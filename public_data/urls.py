from django.conf.urls import url
from django.views.decorators.http import require_POST
from django.views.generic import TemplateView

from common.decorators import participant_required

from .views import (ConsentView, HomeView, QuizView,
                    ToggleSharingView, WithdrawView)


urlpatterns = [
    url(r'^$', HomeView.as_view(), name='home'),

    # Is this here so we can link to the consent form for anonymous visitors?
    url(r'^consent/',
        TemplateView.as_view(template_name='public_data/consent.html'),
        name='consent'),

    # Enrollment process pages. User must be logged in to access.
    url(r'^enroll-1-overview',
        participant_required(
            TemplateView.as_view(template_name='public_data/overview.html')),
        name='enroll-overview'),
    url(r'^enroll-2-consent', ConsentView.as_view(), name='enroll-consent'),
    url(r'^enroll-3-quiz', QuizView.as_view(), name='enroll-quiz'),
    url(r'^enroll-4-signature',
        require_POST(ConsentView.as_view()),
        name='enroll-signature'),

    # Withdraw from the public data study
    url(r'^withdraw', WithdrawView.as_view(), name='withdraw'),

    # Data management
    url(r'^toggle-sharing/',
        ToggleSharingView.as_view(),
        name='toggle-sharing'),
]
