from django.conf import settings
from django.conf.urls import patterns, include, url
from django.conf.urls.static import static  # XXX: Best way to do this?
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse_lazy
from django.views.generic import TemplateView

from .views import (SignupView, DatasetsView, ExceptionView,
                    ProfileDetailView, ProfileListView,
                    UserProfileDashboardView, UserProfileEditView,
                    UserSettingsEditView)

from . import api_urls

import studies.urls
import activities.urls

urlpatterns = patterns(
    '',

    url('', include('social.apps.django_app.urls', namespace='social')),

    url(r'^admin/', include(admin.site.urls)),

    # Include the various APIs here
    url(r'^api/', include(studies.urls)),
    url(r'^api/', include(api_urls)),

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

    # Login should return to this page. I tried reverse_lazy but that led
    # to an recursion error, hah. Needs better general soln.  - Madeleine
    url(r'^public-data-sharing/$',
        TemplateView.as_view(template_name='pages/public-data-sharing.html'),
        {'next': '/public-data-sharing/'},
        name='public-data-sharing'),

    # Override because we use a custom form with custom view.
    url(r'^account/signup/$', SignupView.as_view(), name='account_signup'),
    # This has to be after the overriden account/ URLs, not before
    url(r'^account/', include('account.urls')),

    url(r'^members/$',
        ProfileListView.as_view(),
        name='profile_list'),

    url(r'^members/(?P<slug>[A-Za-z_0-9]+)/$',
        ProfileDetailView.as_view(),
        name='profile_detail'),

    url(r'^profile/$', login_required(UserProfileDashboardView.as_view()),
        name='profile_dashboard'),

    url(r'^profile/edit/$', login_required(UserProfileEditView.as_view()),
        name='profile_edit'),

    url(r'^profile/research_data/$',
        login_required(DatasetsView.as_view()),
        name='profile_research_data'),

    url(r'^profile/account_settings/$',
        login_required(UserSettingsEditView.as_view()),
        name='profile_account_settings'),

    url(r'^profile/signup_setup/$',
        login_required(UserSettingsEditView.as_view(
            template_name='profile/signup_setup.html',
            success_url=reverse_lazy('signup_setup_2'),
            initial={'submit_value': 'Save and continue'},
        )),
        name='signup_setup'),

    url(r'^profile/signup_setup_2/$',
        login_required(UserProfileEditView.as_view(
            template_name='profile/signup_setup_2.html',
            success_url=reverse_lazy('profile_research_data'),
            initial={'submit_value': 'Save and continue'},
            )),
        name='signup_setup_2'),

) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += patterns(
        '',

        url(r'^raise-exception/$', ExceptionView.as_view()),
    )
