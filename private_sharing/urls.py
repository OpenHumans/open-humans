from django.conf.urls import url
from django.views.generic import TemplateView

from .views import CreateOAuth2DataRequestActivityView

urlpatterns = [
    url(r'^$',
        TemplateView.as_view(
            template_name='private_sharing/applications.html'),
        name='applications'),

    url(r'^create/oauth2/$',
        CreateOAuth2DataRequestActivityView.as_view(),
        name='create-oauth2'),

    url(r'^create/on-site/$',
        TemplateView.as_view(
            template_name='private_sharing/create-on-site.html'),
        name='create-on-site'),

    url(r'^manage/$',
        TemplateView.as_view(
            template_name='private_sharing/manage.html'),
        name='manage-applications'),

    url(r'^edit/oauth2/(?P<slug>[A-Za-z_0-9]+)/$',
        TemplateView.as_view(
            template_name='private_sharing/edit-oauth2.html'),
        name='edit-oauth2'),

    url(r'^edit/on-site/(?P<slug>[A-Za-z_0-9]+)/$',
        TemplateView.as_view(
            template_name='private_sharing/edit-on-site.html'),
        name='edit-on-site'),

    url(r'^in-development/$',
        TemplateView.as_view(
            template_name='private_sharing/in-development.html'),
        name='in-development'),
]
