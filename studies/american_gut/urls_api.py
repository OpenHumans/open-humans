from django.conf.urls import url

from rest_framework.urlpatterns import format_suffix_patterns

from .views import (BarcodeDetail, BarcodeList, SurveyIdDetail, SurveyIdList,
                    UserDataDetail)

urlpatterns = [
    url(r'^user-data/$', UserDataDetail.as_view()),

    url(r'^barcodes/$', BarcodeList.as_view()),
    url(r'^barcodes/(?P<pk>[0-9]+)/$', BarcodeDetail.as_view()),

    url(r'^survey-ids/$', SurveyIdList.as_view()),
    url(r'^survey-ids/(?P<pk>[0-9]+)/$', SurveyIdDetail.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)
