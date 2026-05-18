#!/bin/bash

# Exit on error
set -e

echo "Waiting for PostgreSQL to be ready..."
# The depends_on condition: service_healthy in compose usually handles this,
# but it's good practice to also check at the application level if running standalone.

echo "Running Database Migrations..."
alembic upgrade head

echo "Starting FastAPI Server..."
exec uvicorn src.app.main:app --host 0.0.0.0 --port 8000 --reload
