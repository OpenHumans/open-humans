from django_hosts import patterns, host

host_patterns = patterns(
    'open_humans',

    host(r'research', 'urls_research', name='research'),
    host(r'', 'urls', name='main'),
)
