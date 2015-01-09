from django.conf.urls import url

from rest_framework.urlpatterns import format_suffix_patterns

from .views import GoViralIdList, UserDataDetail

urlpatterns = [
    url(r'^user-data/$', UserDataDetail.as_view()),
    url(r'^ids/$', GoViralIdList.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)
