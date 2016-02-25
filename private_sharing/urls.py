from django.conf.urls import url
from django.views.generic import TemplateView

from . import views

urlpatterns = [
    url(r'^overview/$', views.OverviewView.as_view(), name='overview'),

    url(r'^apps/create/$',
        TemplateView.as_view(template_name='private_sharing/choose-type.html'),
        name='choose-type'),

    url(r'^apps/oauth2/create/$',
        views.CreateOAuth2DataRequestActivityView.as_view(),
        name='create-oauth2'),

    url(r'^apps/on-site/create/$',
        views.CreateOnSiteDataRequestActivityView.as_view(),
        name='create-on-site'),

    url(r'^apps/oauth2/update/(?P<pk>[0-9]+)/$',
        views.UpdateOAuth2DataRequestActivityView.as_view(),
        name='update-oauth2'),

    url(r'^apps/on-site/update/(?P<pk>[0-9]+)/$',
        views.UpdateOnSiteDataRequestActivityView.as_view(),
        name='update-on-site'),

    url(r'^apps/manage/$',
        views.ManageDataRequestActivitiesView.as_view(),
        name='manage-applications'),

    url(r'^in-development/$',
        TemplateView.as_view(
            template_name='private_sharing/in-development.html'),
        name='in-development'),
]
