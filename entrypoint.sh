#!/bin/bash

# Run migrations
echo "Running migrations..."
flask db upgrade

# Start the flask application
echo "Starting the Flask application..."
exec gunicorn -w 4 -b 0.0.0.0:5050 run:app