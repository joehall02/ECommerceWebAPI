#!/bin/bash
set -e # Exit immediately if a command exits with a non-zero status

# Use docker compose role if provided, otherwise default to SERVICE_ROLE environment variable
ROLE=${1:-$SERVICE_ROLE}

echo "Running entrypoint script for role: $ROLE"

if [ "$ROLE" == "backend" ]; then
    # Recreate service account file from environment variable
    if [ -n "$GOOGLE_SERVICE_ACCOUNT_B64" ]; then
        echo "Recreating service account file..."
        echo "$GOOGLE_SERVICE_ACCOUNT_B64" | base64 -d > service-account-file.json
    else
        echo "GOOGLE_SERVICE_ACCOUNT_B64 is not set. Skipping service account file recreation."
    fi
    
    # Run migration
    echo "Running migrations..."
    flask db upgrade
    
    # Start the flask application
    echo "Starting Gunicorn..."
    exec gunicorn -w $GUNICORN_WORKERS -b 0.0.0.0:${PORT:-5050} run:app

elif [ "$ROLE" == "celery" ]; then
    # Start the Celery worker
    echo "Starting Celery worker..."
    exec celery -A celery_worker.celery worker --loglevel=info --concurrency=$CELERY_WORKER_CONCURRENCY

elif [ "$ROLE" == "beat" ]; then
    # Start the Celery beat scheduler
    echo "Starting Celery beat..."
    exec celery -A celery_worker.celery beat --scheduler redbeat.RedBeatScheduler

else
    echo "Invalid role specified. Please use 'backend', 'celery', or 'beat'."
    exit 1
fi