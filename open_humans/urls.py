from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.generic import TemplateView

urlpatterns = patterns(
    '',

    url(r'^admin/', include(admin.site.urls)),

    url(r'^$', TemplateView.as_view(template_name='home.html')),
    url(r'^about/$', TemplateView.as_view(template_name='about.html')),
    url(r'^dashboard/$', TemplateView.as_view(template_name='dashboard.html')),

    url(r'^accounts/login/$', 'django.contrib.auth.views.login',
        {'template_name': 'login.html'}),

    url(r'^accounts/logout/$', 'django.contrib.auth.views.logout'),
)
