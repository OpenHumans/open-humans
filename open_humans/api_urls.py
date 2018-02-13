from django.conf.urls import url

from rest_framework.urlpatterns import format_suffix_patterns

from . import api_views

urlpatterns = [
    url(r'^member/$', api_views.MemberDetailAPIView.as_view()),

    url(r'^public-data/$',
        api_views.PublicDataListAPIView.as_view(),
        name='public-data'),

    url(r'^public-data/members/$',
        api_views.PublicDataMembers.as_view()),

    url(r'^public-data/sources-by-member/$',
        api_views.PublicDataSourcesByUserAPIView.as_view()),

    url(r'^public-data/members-by-source/$',
        api_views.PublicDataUsersBySourceAPIView.as_view(),
        name='members-by-source'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
