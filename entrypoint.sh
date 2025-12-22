#!/bin/bash
set -e

echo "=== Entrypoint starting ==="
echo "Waiting for database to be ready..."

# Create migrations if needed
python3 manage.py makemigrations --noinput 2>/dev/null || true

echo "=== Running migrations ==="
python3 manage.py migrate || echo "WARNING: Migrations failed, continuing anyway..."
echo "=== Migrations done ==="

echo "=== Collecting static files ==="
python3 manage.py collectstatic --noinput || true
echo "=== Collectstatic done ==="

# Use PORT environment variable or default to 8000 (Azure App Service default)
PORT=${PORT:-8000}
echo "=== Starting gunicorn on port $PORT ==="
echo "Command: gunicorn --bind 0.0.0.0:$PORT girjasoft.wsgi:application"

# Keep gunicorn in foreground with logging
exec gunicorn --bind 0.0.0.0:$PORT --access-logfile - --error-logfile - --log-level info girjasoft.wsgi:application
