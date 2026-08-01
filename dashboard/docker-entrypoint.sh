#!/bin/sh
set -e

export DOCKER=true

mkdir -p /app/data

python manage.py migrate
python manage.py ensure_admin

# Run check_status every 5 seconds in background
(
  while true; do
    python manage.py check_status
    sleep 5
  done
) &

exec gunicorn escape_room_dashboard.wsgi:application --bind 0.0.0.0:8000
