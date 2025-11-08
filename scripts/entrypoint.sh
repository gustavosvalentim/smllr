#!/bin/sh

# Handle django static files
python manage.py collectstatic --noinput

# Run database migrations
python manage.py migrate --noinput

# Start the gunicorn server
$@ 
