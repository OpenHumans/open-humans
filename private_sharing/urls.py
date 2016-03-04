from django.conf.urls import url
from django.views.generic import TemplateView

from . import views

urlpatterns = [
    url(r'^overview/$', views.OverviewView.as_view(), name='overview'),

    url(r'^projects/oauth2/create/$',
        views.CreateOAuth2DataRequestProjectView.as_view(),
        name='create-oauth2'),

    url(r'^projects/on-site/create/$',
        views.CreateOnSiteDataRequestProjectView.as_view(),
        name='create-on-site'),

    url(r'^projects/oauth2/(?P<pk>[0-9]+)/$',
        views.OAuth2DataRequestProjectDetailView.as_view(),
        name='detail-oauth2'),

    url(r'^projects/on-site/(?P<pk>[0-9]+)/$',
        views.OnSiteDataRequestProjectDetailView.as_view(),
        name='detail-on-site'),

    url(r'^projects/on-site/join/(?P<pk>[0-9]+)/$',
        views.JoinOnSiteDataRequestProjectView.as_view(),
        name='join-on-site'),

    url(r'^projects/on-site/authorize/(?P<pk>[0-9]+)/$',
        views.AuthorizeOnSiteDataRequestProjectView.as_view(),
        name='authorize-on-site'),

    url(r'^projects/oauth2/update/(?P<pk>[0-9]+)/$',
        views.UpdateOAuth2DataRequestProjectView.as_view(),
        name='update-oauth2'),

    url(r'^projects/on-site/update/(?P<pk>[0-9]+)/$',
        views.UpdateOnSiteDataRequestProjectView.as_view(),
        name='update-on-site'),

    url(r'^projects/manage/$',
        views.ManageDataRequestActivitiesView.as_view(),
        name='manage-projects'),

    url(r'^in-development/$',
        TemplateView.as_view(
            template_name='private_sharing/in-development.html'),
        name='in-development'),
]
