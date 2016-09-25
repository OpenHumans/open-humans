from django.conf.urls import url

from rest_framework.urlpatterns import format_suffix_patterns

from . import api_views

urlpatterns = [
    url(r'^project/$', api_views.ProjectDataView.as_view()),
    url(r'^project/members/$', api_views.ProjectMemberDataView.as_view()),
    url(r'^project/exchange-member/$',
        api_views.ProjectMemberExchangeView.as_view()),
    url(r'^project/message/$', api_views.ProjectMessageView.as_view()),

    # Views for managing uploaded data files
    url(r'^project/files/upload/$', api_views.ProjectFileUploadView.as_view()),
    url(r'^project/files/delete/$', api_views.ProjectFileDeleteView.as_view()),

    url(r'^project/files/upload/direct/$',
        api_views.ProjectFileDirectUploadView.as_view()),

    url(r'^project/files/upload/complete/$',
        api_views.ProjectFileDirectUploadCompletionView.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)
