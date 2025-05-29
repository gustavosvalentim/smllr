python manage.py migrate --noinput

python manage.py collectstatic --noinput

gunicorn --workers 4 --bind 0.0.0.0:8000 smllr.wsgi