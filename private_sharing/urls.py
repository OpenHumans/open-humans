from django.conf.urls import url
from django.views.generic import TemplateView

from .views import (CreateOAuth2DataRequestActivityView,
                    CreateOnSiteDataRequestActivityView,
                    OverviewView)

urlpatterns = [
    url(r'^overview/$', OverviewView.as_view(), name='overview'),

    url(r'^applications/$',
        TemplateView.as_view(template_name='private_sharing/applications.html'),
        name='applications'),

    url(r'^create-app/$',
        TemplateView.as_view(template_name='private_sharing/choose-type.html'),
        name='choose-type'),

    url(r'^create-app/oauth2/$',
        CreateOAuth2DataRequestActivityView.as_view(),
        name='create-oauth2'),

    url(r'^create-app/on-site/$',
        CreateOnSiteDataRequestActivityView.as_view(),
        name='create-on-site'),

    # TODO: write a view that lists a member's applications for management
    url(r'^manage/$',
        TemplateView.as_view(template_name='private_sharing/manage.html'),
        name='manage-applications'),

    url(r'^edit/oauth2/(?P<slug>[A-Za-z_0-9]+)/$',
        TemplateView.as_view(template_name='private_sharing/edit-oauth2.html'),
        name='edit-oauth2'),

    url(r'^edit/on-site/(?P<slug>[A-Za-z_0-9]+)/$',
        TemplateView.as_view(template_name='private_sharing/edit-on-site.html'),
        name='edit-on-site'),

    url(r'^in-development/$',
        TemplateView.as_view(
            template_name='private_sharing/in-development.html'),
        name='in-development'),
]
