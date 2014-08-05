from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views

from .views import UserCreateView, UserProfileDetailView, UserProfileEditView

urlpatterns = patterns(
    '',

    url(r'^admin/', include(admin.site.urls)),

    url(r'^$', TemplateView.as_view(template_name='home.html'), name='home'),
    url(r'^about/$', TemplateView.as_view(template_name='about.html'),
        name='about'),
    url(r'^dashboard/$', TemplateView.as_view(template_name='dashboard.html'),
        name='dashboard'),

    url(r'^accounts/signup/$', UserCreateView.as_view(),
        name='accounts-signup'),

    url(r'^accounts/login/$', auth_views.login,
        {'template_name': 'login.html'},
        name='accounts-login'),

    url(r'^accounts/logout/$', auth_views.logout, {'next_page': '/'},
        name='accounts-logout'),

    url(r'^profile/$', login_required(UserProfileDetailView.as_view()),
        name='profile-detail'),

    url(r'^profile/edit/$', login_required(UserProfileEditView.as_view()),
        name='profile-edit'),
)
