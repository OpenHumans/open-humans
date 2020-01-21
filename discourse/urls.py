from django.conf.urls import url

from .views import single_sign_on

urlpatterns = [url(r"^sso/$", single_sign_on)]
