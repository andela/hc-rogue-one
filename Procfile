web: gunicorn hc.wsgi:application
worker: celery worker -A hc -E -l info