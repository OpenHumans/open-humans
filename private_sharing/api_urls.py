from django.conf.urls import url

from rest_framework.urlpatterns import format_suffix_patterns

from . import api_views

urlpatterns = [
    url(r'^project/$', api_views.ProjectDataView.as_view()),
    url(r'^project/members/$', api_views.ProjectMemberDataView.as_view()),
    url(r'^project/exchange-member/$',
        api_views.ProjectMemberExchangeView.as_view()),
    url(r'^project/message/$', api_views.ProjectMessageView.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)
