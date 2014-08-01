from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views

from .views import UserCreateView

urlpatterns = patterns(
    '',

    url(r'^admin/', include(admin.site.urls)),

    url(r'^$', TemplateView.as_view(template_name='home.html')),
    url(r'^about/$', TemplateView.as_view(template_name='about.html')),
    url(r'^dashboard/$', TemplateView.as_view(template_name='dashboard.html')),

    url(r'^accounts/signup/$', UserCreateView.as_view(), name='auth_signup'),

    url(r'^accounts/login/$', auth_views.login,
        {'template_name': 'home.html'}, name='auth_login'),

    url(r'^accounts/logout/$', auth_views.logout, {'next_page': '/'},
        name='auth_logout'),
)
