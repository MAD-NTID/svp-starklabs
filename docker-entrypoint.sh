#!/bin/sh
set -e

export DOCKER=true

mkdir -p /app/data

python manage.py migrate
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
"

# Run check_status every 10 seconds in background
(
  while true; do
    python manage.py check_status
    sleep 10
  done
) &

exec gunicorn escape_room_dashboard.wsgi:application --bind 0.0.0.0:8000
