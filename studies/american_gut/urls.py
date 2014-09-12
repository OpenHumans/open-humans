from django.conf.urls import patterns, url

from rest_framework.urlpatterns import format_suffix_patterns

from . import views

urlpatterns = patterns(
    '',

    url(r'^barcodes/$', views.BarcodeList.as_view()),
)

urlpatterns = format_suffix_patterns(urlpatterns)
