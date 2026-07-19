#!/bin/bash
# Pre-production / Production startup script for MoneyMan WebApp

# Exit on error
set -e

# Load virtual environment if it exists
if [ -d ".venv" ]; then
    echo "Activating virtual environment..."
    source .venv/bin/activate
fi

# Set default configuration environment variables
export PORT=${PORT:-5050}
# Generate a random 32-byte secret key if not provided
if [ -z "$SECRET_KEY" ]; then
    export SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(32))')
fi
export DATABASE_PATH=${DATABASE_PATH:-$(pwd)/moneyman.db}
export GEMINI_API_KEY=${GEMINI_API_KEY:-""}

echo "========================================="
echo "Starting MoneyMan WebApp in Pre-Production"
echo "Port: $PORT"
echo "Database: $DATABASE_PATH"
echo "========================================="

# Start the application using gunicorn WSGI server
exec gunicorn -w 4 -b 0.0.0.0:$PORT app:app
