from django.conf.urls import patterns, url

from .views import TaskUpdateView

urlpatterns = patterns(
    '',

    url(r'^task_update/', TaskUpdateView.as_view()),
)
