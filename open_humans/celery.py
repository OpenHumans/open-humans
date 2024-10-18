import os

from django.conf import settings

from celery import Celery


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "open_humans.settings")

app = Celery("open_humans")


app.conf.update(
    {
        "BROKER_URL": settings.CELERY_BROKER_URL,
        # Recommended settings. See: https://www.cloudamqp.com/docs/celery.html
        "BROKER_POOL_LIMIT": None,
        "BROKER_HEARTBEAT": None,
        "BROKER_CONNECTION_TIMEOUT": 30,
        "CELERY_RESULT_BACKEND": settings.CELERY_BROKER_URL,
        "CELERY_SEND_EVENTS": False,
        "CELERY_EVENT_QUEUE_EXPIRES": 60,
    }
)
app.config_from_object("django.conf:settings", namespace="CELERY")

if os.getenv("ON_HEROKU"):
    # if running on Heroku, set the redis_backend_use_ssl config var
    app.conf.redis_backend_use_ssl = {"ssl_cert_reqs": "none"}

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print("Request: {0!r}".format(self.request))
