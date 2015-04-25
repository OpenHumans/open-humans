"""
URLs used by research.openhumans.org, where Researchers interact with the site.
"""

from django.conf import settings
from django.conf.urls import include, patterns, url
from django.conf.urls.static import static  # XXX: Best way to do this?
from django.views.generic import TemplateView

from account.views import LogoutView as AccountLogoutView

from .views import ResearcherLoginView, ResearcherSignupView

urlpatterns = patterns(
    '',

    url(r'^$', TemplateView.as_view(template_name='research/home.html'),
        name='home'),
    # Override to use custom form and view with added fields and methods.
    url(r'^account/signup/$', ResearcherSignupView.as_view(),
        name='account_signup'),
    url(r'^account/login/$', ResearcherLoginView.as_view(),
        name='account_login'),
    url(r'^account/logout/$', AccountLogoutView.as_view(
        template_name='research/account/logout.html'), name='account_logout'),
    url(r'^account/create/$',
        TemplateView.as_view(template_name='research/account/create.html'),
        name='account_create'),
    url(r'^account/create/$', TemplateView.as_view(
        template_name='research/account/password_reset.html'),
        name='account_password_reset'),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
