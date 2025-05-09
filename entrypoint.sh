#!/bin/bash
set -e # Exit immediately if a command exits with a non-zero status

echo "Running entrypoint script for role: $1"

if [ "$1" == "backend" ]; then
    # Run migration
    echo "Running migrations..."
    flask db upgrade
    
    # Start the flask application
    echo "Starting Gunicorn..."
    exec gunicorn -w 4 -b 0.0.0.0:5050 run:app

elif [ "$1" == "celery" ]; then
    # Start the Celery worker
    echo "Starting Celery worker..."
    exec celery -A celery_worker.celery worker --loglevel=info

elif [ "$1" == "beat" ]; then
    # Start the Celery beat scheduler
    echo "Starting Celery beat..."
    exec celery -A celery_worker.celery beat --scheduler redbeat.RedBeatScheduler

else
    echo "Invalid role specified. Please use 'backend', 'celery', or 'beat'."
    exit 1
fi