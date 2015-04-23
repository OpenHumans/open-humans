"""
URLs used by research.openhumans.org, where Researchers interact with the site.
"""

from django.conf import settings
from django.conf.urls import include, patterns, url
from django.conf.urls.static import static  # XXX: Best way to do this?
from django.views.generic import TemplateView

urlpatterns = patterns(
    '',

    url(r'^$', TemplateView.as_view(template_name='research/home.html'),
        name='home'),
    url(r'^account/', include('account.urls')),

) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
