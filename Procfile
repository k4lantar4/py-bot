web: cd backend && python manage.py migrate && python manage.py collectstatic --no-input && gunicorn config.wsgi --log-file -
worker: cd backend && celery -A config worker --loglevel=info
beat: cd backend && celery -A config beat --loglevel=info 