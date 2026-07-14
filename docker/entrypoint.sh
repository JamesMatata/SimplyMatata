#!/bin/sh
set -e

MEDIA_DIRS="
/app/media/projects/thumbnails
/app/media/projects/featured
/app/media/projects/media
/app/media/projects/comics
/app/media/projects/episodes/thumbnails
/app/media/projects/episodes/featured
"

if [ "$(id -u)" = "0" ]; then
    for dir in $MEDIA_DIRS; do
        mkdir -p "$dir"
    done
    chown -R app:app /app/media
fi

run_as_app() {
    if [ "$(id -u)" = "0" ]; then
        gosu app "$@"
    else
        "$@"
    fi
}

echo "Waiting for database..."
run_as_app python - <<'PY'
import os
import sys
import time

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django

django.setup()

from django.db import connection
from django.db.utils import OperationalError

for attempt in range(30):
    try:
        connection.ensure_connection()
        break
    except OperationalError:
        time.sleep(1)
else:
    sys.exit("Database is unavailable after 30 seconds.")
PY

echo "Running migrations..."
run_as_app python manage.py migrate --noinput

echo "Starting gunicorn..."
if [ "$(id -u)" = "0" ]; then
    exec gosu app gunicorn config.wsgi:application \
        --bind "0.0.0.0:${PORT:-8000}" \
        --workers "${WEB_CONCURRENCY:-3}" \
        --timeout 120 \
        --access-logfile - \
        --error-logfile -
fi

exec gunicorn config.wsgi:application \
    --bind "0.0.0.0:${PORT:-8000}" \
    --workers "${WEB_CONCURRENCY:-3}" \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -
