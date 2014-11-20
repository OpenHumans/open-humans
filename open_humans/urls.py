from django.conf import settings
from django.conf.urls import patterns, include, url
from django.conf.urls.static import static  # XXX: Best way to do this?
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse_lazy
from django.views.generic import TemplateView

from .views import (SignupView, DatasetsView, ExceptionView,
                    MemberProfileDetailView, MemberProfileListView,
                    PasswordResetView, PasswordResetTokenView,
                    UserProfileDashboardView, UserProfileEditView,
                    UserSettingsEditView)

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

    # Login should return to this page. I tried reverse_lazy but that led
    # to an recursion error, hah. Needs better general soln.  - Madeleine
    url(r'^public-data-sharing/$',
        TemplateView.as_view(template_name='pages/public-data-sharing.html'),
        {'next': '/public-data-sharing/'},
        name='public-data-sharing'),

    # Override because we use some custom forms with custom views.
    url(r'^account/signup/$', SignupView.as_view(), name='account_signup'),
    url(r'^account/password/reset/$', PasswordResetView.as_view(),
        name='account_password_reset'),
    url(r"^account/password/reset/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$",
        PasswordResetTokenView.as_view(), name="account_password_reset_token"),
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
