#!/bin/sh

set -e

# Install dependencies if not already installed
pip install --no-cache-dir -r requirements.txt

# Make sure PYTHONPATH is set correctly
export PYTHONPATH=${PYTHONPATH:-/app}

# Try to use the standard settings, but fall back to test_settings if needed
if [ -z "$DJANGO_SETTINGS_MODULE" ]; then
    export DJANGO_SETTINGS_MODULE=config.settings
    # Try to import the settings, if it fails, fall back to test_settings
    python -c "from django.conf import settings" 2>/dev/null || export DJANGO_SETTINGS_MODULE=config.test_settings
fi

echo "🚀 Using settings module: $DJANGO_SETTINGS_MODULE"

# Wait for PostgreSQL to be ready
echo "⏳ Waiting for PostgreSQL..."
python -m scripts.wait_for_postgres

# Wait for Redis to be ready
echo "⏳ Waiting for Redis..."
python -m scripts.wait_for_redis

# Run migrations
echo "🔄 Running migrations..."
python manage.py migrate --noinput

# Collect static files
echo "📦 Collecting static files..."
python manage.py collectstatic --noinput

# Create superuser if necessary
if [ "$CREATE_SUPERUSER" = "true" ]; then
    echo "👤 Creating superuser..."
    python -c "
import os
from django.contrib.auth import get_user_model;
User = get_user_model();
username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin');
email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@example.com');
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'adminpassword');
if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username, email, password);
    print(f'Superuser {username} created');
else:
    print(f'Superuser {username} already exists');
"
fi

# Execute the command passed to the entrypoint
echo "🌟 Starting $@..."
exec "$@" 