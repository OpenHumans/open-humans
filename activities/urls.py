from django.conf.urls import include, patterns, url
from django.views.generic import TemplateView

import twenty_three_and_me.urls

urlpatterns = patterns(
    '',
    url(r'^23andme/', include(twenty_three_and_me.urls, namespace='23andme')),
    url(r'^quijibo/',
        TemplateView.as_view(template_name='twenty_three_and_me/complete-import-23andme.html'),
        name='complete-import'),
)
