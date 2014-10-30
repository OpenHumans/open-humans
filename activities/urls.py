from django.conf.urls import include, patterns, url

from .views import TaskUpdateView

import twenty_three_and_me.urls

urlpatterns = patterns(
    '',
    url(r'^23andme/', include(twenty_three_and_me.urls, namespace='23andme')),
    url(r'^task_update/', TaskUpdateView.as_view()),
)
