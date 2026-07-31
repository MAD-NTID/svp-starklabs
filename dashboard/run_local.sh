#!/bin/sh
set -e

python manage.py migrate
python manage.py ensure_admin
exec python manage.py runserver "$@"
