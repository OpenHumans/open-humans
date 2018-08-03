from common.decorators import participant_required

from django.urls import path
from django.views.decorators.http import require_POST
from django.views.generic import TemplateView

from .views import (ConsentView, HomeView, QuizView,
                    ToggleSharingView, WithdrawView)

app_name = 'public-data'


urlpatterns = [
    path('', HomeView.as_view(), name='home'),

    # Enrollment process pages. User must be logged in to access.
    path('activate-1-overview/',
         participant_required(
             TemplateView.as_view(template_name='public_data/overview.html')),
         name='enroll-overview'),
    path('activate-2-information/', ConsentView.as_view(),
         name='enroll-information'),
    path('activate-3-quiz/', QuizView.as_view(), name='enroll-quiz'),
    path('activate-4-complete/',
         require_POST(ConsentView.as_view()),
         name='enroll-signature'),

    # Withdraw from the public data study
    path('deactivate/', WithdrawView.as_view(), name='deactivate'),

    # Data management
    path('toggle-sharing/',
         ToggleSharingView.as_view(),
         name='toggle-sharing'),
]
