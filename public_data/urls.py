from django.conf.urls import url
from django.views.decorators.http import require_POST
from django.views.generic import TemplateView

from common.decorators import participant_required

from .views import (ConsentView, HomeView, QuizView,
                    ToggleSharingView, WithdrawView)


urlpatterns = [
    url(r'^$', HomeView.as_view(), name='home'),

    # Enrollment process pages. User must be logged in to access.
    url(r'^activate-1-overview',
        participant_required(
            TemplateView.as_view(template_name='public_data/overview.html')),
        name='enroll-overview'),
    url(r'^activate-2-information', ConsentView.as_view(),
        name='enroll-information'),
    url(r'^activate-3-quiz', QuizView.as_view(), name='enroll-quiz'),
    url(r'^activate-4-complete',
        require_POST(ConsentView.as_view()),
        name='enroll-signature'),

    # Withdraw from the public data study
    url(r'^deactivate', WithdrawView.as_view(), name='deactivate'),

    # Data management
    url(r'^toggle-sharing/',
        ToggleSharingView.as_view(),
        name='toggle-sharing'),
]
