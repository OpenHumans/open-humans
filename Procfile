web: gunicorn open_humans.wsgi
worker: celery -A open_humans worker --concurrency 1 -l info
