from django.views.decorators.cache import cache_page


class CacheMixin(object):
    """
    Cache the page for the given cache_timeout.
    """
    cache_timeout = 60

    def get_cache_timeout(self):
        return self.cache_timeout

    def dispatch(self, *args, **kwargs):
        return cache_page(self.get_cache_timeout())(
            super(CacheMixin, self).dispatch)(*args, **kwargs)
