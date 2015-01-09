from django.conf.urls import url

from rest_framework.urlpatterns import format_suffix_patterns

from .views import MemberDetail

urlpatterns = [
    url(r'^member/$', MemberDetail.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)
