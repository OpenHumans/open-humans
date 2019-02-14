from django.urls import path

from rest_framework.urlpatterns import format_suffix_patterns

from . import api_views

urlpatterns = [
    path('project/', api_views.ProjectDataView.as_view()),
    path('project/members/', api_views.ProjectMemberDataView.as_view()),
    path('project/exchange-member/', api_views.ProjectMemberExchangeView.as_view()),
    path('project/message/', api_views.ProjectMessageView.as_view()),
    path('project/remove-members/', api_views.ProjectRemoveMemberView.as_view()),
    # Views for managing uploaded data files
    path('project/files/upload/', api_views.ProjectFileUploadView.as_view()),
    path('project/files/delete/', api_views.ProjectFileDeleteView.as_view()),
    path(
        'project/files/upload/direct/', api_views.ProjectFileDirectUploadView.as_view()
    ),
    path(
        'project/files/upload/complete/',
        api_views.ProjectFileDirectUploadCompletionView.as_view(),
    ),
]

urlpatterns = format_suffix_patterns(urlpatterns)
