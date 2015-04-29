from django.conf import settings
from django_hosts import patterns, host

host_patterns = patterns(
    '',

    host(settings.RESEARCH_HOST, 'studies.urls_research', name='research'),
    host(r'', 'open_humans.urls', name='main'),
)
