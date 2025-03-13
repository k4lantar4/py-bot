#!/bin/bash

set -e

host="${DB_HOST:-db}"
port="${DB_PORT:-5432}"

# Function to check if postgres is ready
postgres_ready() {
    nc -z "$host" "$port"
}

# Function to check if redis is ready
redis_ready() {
    nc -z "${REDIS_HOST:-redis}" "${REDIS_PORT:-6379}"
}

# Wait for postgres
until postgres_ready; do
  >&2 echo "Waiting for PostgreSQL on $host:$port..."
  sleep 1
done
>&2 echo "PostgreSQL is up and running on $host:$port!"

# Wait for redis
until redis_ready; do
  >&2 echo "Waiting for Redis..."
  sleep 1
done
>&2 echo "Redis is up!"

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate --noinput

# Create default superuser if needed
if [ "$DJANGO_SUPERUSER_USERNAME" ] && [ "$DJANGO_SUPERUSER_EMAIL" ] && [ "$DJANGO_SUPERUSER_PASSWORD" ]; then
    echo "Creating/Updating superuser..."
    python manage.py shell -c "
from django.contrib.auth import get_user_model;
User = get_user_model();
User.objects.update_or_create(
    username='$DJANGO_SUPERUSER_USERNAME',
    defaults={
        'email': '$DJANGO_SUPERUSER_EMAIL',
        'is_superuser': True,
        'is_staff': True
    }
)[0].set_password('$DJANGO_SUPERUSER_PASSWORD')"
fi

# Import default messages if running bot
if [[ "$*" == *"telegram.main"* ]]; then
    echo "Importing default messages..."
    python manage.py import_default_messages --overwrite
    
    echo "Setting up initial bot settings..."
    python manage.py shell -c "
from telegram.models import BotSetting;
BotSetting.objects.get_or_create(
    key='referral_bonus_amount',
    defaults={
        'value': '10000',
        'description': 'Referral bonus amount in Toman',
        'is_public': True
    }
)"
fi

# Execute the command
exec "$@" 