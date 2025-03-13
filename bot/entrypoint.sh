#!/bin/bash

# Wait for backend to be ready
echo "Waiting for backend..."
# Temporarily skip backend check for local testing
# until $(curl --output /dev/null --silent --head --fail http://backend:8000/health); do
#     printf '.'
#     sleep 5
# done
echo "Backend check skipped for local testing!"

# Start bot
echo "Starting bot..."
exec "$@" 