#!/bin/bash

# Wait for database to be ready
echo "Waiting for database..."
while ! nc -z ${DB_HOST} ${DB_PORT}; do
  sleep 1
done
echo "Database is ready!"

# Apply database migrations
echo "Applying migrations..."
python manage.py migrate --noinput

# Create superuser if needed
python manage.py createsuperuser --noinput || echo "Superuser already exists or couldn't be created."

exec "$@" 