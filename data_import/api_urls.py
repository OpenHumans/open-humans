from django.urls import path

from rest_framework.urlpatterns import format_suffix_patterns

from . import api_views

urlpatterns = [path("datatypes/", api_views.DataTypesListAPIView.as_view())]

urlpatterns = format_suffix_patterns(urlpatterns)
