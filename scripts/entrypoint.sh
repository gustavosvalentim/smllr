python manage.py migrate --noinput

gunicorn --workers 4 --bind 0.0.0.0:8000 smllr.wsgi