from django.conf.urls import url

from rest_framework.urlpatterns import format_suffix_patterns

from .views import HuIdDetail, HuIdList, UserDataDetail

urlpatterns = [
    url(r'^user-data/$', UserDataDetail.as_view()),
    url(r'^huids/$', HuIdList.as_view()),
    url(r'^huids/(?P<pk>hu[0-9A-F]+)/$', HuIdDetail.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)
