from django.conf.urls import include, patterns, url

from .views import TaskUpdateView

from .twenty_three_and_me import urls as twenty_three_and_me_urls

urlpatterns = patterns(
    '',

    # Activities
    url(r'^23andme/', include(twenty_three_and_me_urls, namespace='23andme')),

    url(r'^task_update/', TaskUpdateView.as_view()),
)
