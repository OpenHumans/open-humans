from django_hosts import patterns, host

host_patterns = patterns(
    '',

    host(r'research', 'studies.urls_research', name='research'),
    host(r'', 'open_humans.urls', name='main'),
)
