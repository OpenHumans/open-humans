from django.conf.urls import patterns, url

from .views import TaskUpdateView

urlpatterns = patterns(
    '',

    url(r'^task-update/', TaskUpdateView.as_view(), name='task-update'),
)
