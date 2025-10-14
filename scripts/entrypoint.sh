#!/bin/sh

# Run database migrations
python manage.py migrate --noinput

# Start the gunicorn server
gunicorn --workers 1 --bind 0.0.0.0:8000 smllr.wsgi
