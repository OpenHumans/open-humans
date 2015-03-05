from django.conf.urls import url

from rest_framework.urlpatterns import format_suffix_patterns

from .views import (BarcodeDetail, BarcodeList, UserDataDetail,
                    DataRetrievalView)

urlpatterns = [
    url(r'^user-data/$', UserDataDetail.as_view()),
    url(r'^barcodes/$', BarcodeList.as_view()),
    url(r'^barcodes/(?P<pk>[0-9]+)/$', BarcodeDetail.as_view()),
    url(r'^request-data-retrieval/$', DataRetrievalView.as_view(),
        name='request-data-retrieval'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
