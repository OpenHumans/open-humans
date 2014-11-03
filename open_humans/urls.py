from django.conf import settings
from django.conf.urls import patterns, include, url
from django.conf.urls.static import static  # XXX: Best way to do this?
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views

from .views import (CustomSignupView, MemberProfileDetailView,
                    MemberProfileListView, UserProfileDashboardView,
                    UserProfileEditView, UserProfileSignupSetup, JSONDataView,
                    DatasetsView)

import studies.urls
import activities.urls

urlpatterns = patterns(
    '',

    url('', include('social.apps.django_app.urls', namespace='social')),

    url(r'^admin/', include(admin.site.urls)),

    # Include the various APIs here
    url(r'^api/', include(studies.urls)),

    # URLs used for activity-related interactions.
    url(r'^activity/', include(activities.urls, namespace='activities')),

    # The URLs used for the OAuth2 dance (e.g. requesting an access token)
    url(r'^oauth2/', include('provider.oauth2.urls', namespace='oauth2')),

    # Simple pages
    url(r'^$', TemplateView.as_view(template_name='pages/home.html'),
        name='home'),
    url(r'^about/$', TemplateView.as_view(template_name='pages/about.html'),
        name='about'),
    url(r'^community_guidelines/$',
        TemplateView.as_view(template_name='pages/community_guidelines.html'),
        name='community_guidelines'),
    url(r'^contact-us/$',
        TemplateView.as_view(template_name='pages/contact_us.html'),
        name='contact_us'),
    url(r'^activities/$',
        TemplateView.as_view(template_name='pages/activities.html'),
        name='activities'),
    url(r'^public-data-sharing/$',
        TemplateView.as_view(template_name='pages/public-data-sharing.html'),
        name='public-data-sharing'),

    # Override signup because we use a custom view
    url(r'^account/signup/$', CustomSignupView.as_view(),
        name='account_signup'),

    # Override login because we use a custom view
    url(r'^account/login/$', auth_views.login, name='account_login'),

    # Override logout because we don't want the user to have to confirm
    url(r'^account/logout/$', auth_views.logout, {'next_page': '/'},
        name='account_logout'),

    # This has to be after the overriden account/ URLs, not before
    url(r'^account/', include('account.urls')),

    url(r'^members/$',
        MemberProfileListView.as_view(),
        name='member_list'),

    url(r'^members/(?P<slug>[A-Za-z_0-9]+)/$',
        MemberProfileDetailView.as_view(),
        name='member_profile'),

    url(r'^profile/$', login_required(UserProfileDashboardView.as_view()),
        name='profile_dashboard'),

    url(r'^profile/edit/$', login_required(UserProfileEditView.as_view()),
        name='profile_edit'),

    url(r'^profile/research_data/$',
        DatasetsView.as_view(),
        name='profile_research_data'),

    url(r'^profile/account_settings/$',
        UserProfileDashboardView.as_view(
            template_name='profile/account_settings.html'),
        name='profile_account_settings'),

    url(r'^profile/signup_setup/$',
        login_required(UserProfileSignupSetup.as_view()),
        name='signup_setup'),
    url(r'^profile/signup_setup_2/$',
        login_required(UserProfileSignupSetup.as_view(
            template_name='profile/signup_setup_2.html')),
        name='signup_setup_2'),

    url(r'^json-data/$',
        login_required(JSONDataView.as_view())),

) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
