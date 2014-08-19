from django.conf import settings
from django.conf.urls import patterns, include, url
from django.conf.urls.static import static  # XXX: Best way to do this?
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views

from .views import CustomSignupView, UserProfileDetailView, UserProfileEditView

urlpatterns = patterns(
    '',

    url(r'^admin/', include(admin.site.urls)),

    url(r'^$', TemplateView.as_view(template_name='home.html'), name='home'),
    url(r'^about/$', TemplateView.as_view(template_name='about.html'),
        name='about'),
    url(r'^dashboard/$', TemplateView.as_view(template_name='dashboard.html'),
        name='dashboard'),

    # Override signup because we use a custom view
    url(r'^account/signup/$', CustomSignupView.as_view(),
        name='account_signup'),

    # Override login because we use a custom view
    url(r'^account/login/$', auth_views.login,
        {'template_name': 'login.html'}, name='account_login'),

    # Override logout because we don't want the user to have to confirm
    url(r'^account/logout/$', auth_views.logout, {'next_page': '/'},
        name='account_logout'),

    # This has to be after the overriden account/ URLs, not before
    url(r'^account/', include('account.urls')),

    url(r'^profile/$', login_required(UserProfileDetailView.as_view()),
        name='profile_detail'),

    url(r'^profile/edit/$', login_required(UserProfileEditView.as_view()),
        name='profile_edit'),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
