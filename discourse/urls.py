from django.urls import re_path

from .views import SingleSignOn

urlpatterns = [re_path(r"^sso/$", SingleSignOn.as_view())]
