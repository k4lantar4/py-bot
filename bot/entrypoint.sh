#!/bin/bash

# Wait for backend to be ready
echo "Waiting for backend..."
until $(curl --output /dev/null --silent --head --fail http://backend:8000/health); do
    printf '.'
    sleep 5
done
echo "Backend is ready!"

# Start bot
echo "Starting bot..."
exec "$@" 