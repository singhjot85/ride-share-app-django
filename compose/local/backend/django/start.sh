#!/bin/bash

set -o errexit
set -o pipefail
set -o nounset

ENABLE_DEBUGPY=${ENABLE_DEBUGPY:-0}
MIGRATE_SCHEMAS=${MIGRATE_SCHEMAS:-0}

if [ "$ENABLE_DEBUGPY" = "1" ]; then
    echo "Migrating schema now..."
    exec python manage.py migrate
fi

echo "Running Django now..."

if [ "$ENABLE_DEBUGPY" = "1" ]; then
    echo "Starting django service with debugpy..."
    exec python -m debugpy --listen 0.0.0.0:5678 manage.py runserver 0.0.0.0:8000
else
    echo "Starting django service..."
    exec python manage.py runserver 0.0.0.0:8000
fi
