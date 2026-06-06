#!/usr/bin/env bash
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# Remove previous DB so every startup is fresh (in-memory semantics)
DB_FILE="${DB_PATH:-/tmp/course_platform_dev.db}"
rm -f "$DB_FILE"
echo "Database reset: $DB_FILE"

venv/bin/python manage.py migrate --run-syncdb
venv/bin/python manage.py seed
exec venv/bin/python manage.py runserver 0.0.0.0:8000
