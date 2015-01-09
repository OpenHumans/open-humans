from django.conf.urls import url

from rest_framework.urlpatterns import format_suffix_patterns

from .views import BarcodeList, UserDataDetail

urlpatterns = [
    url(r'^user-data/$', UserDataDetail.as_view()),
    url(r'^barcodes/$', BarcodeList.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)
