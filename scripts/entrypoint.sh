#!/bin/bash

set -e

if [ -n "${DATABASE_URL:-}" ]; then
  echo "Waiting for PostgreSQL to be ready..."
  until python -c "from sqlalchemy import create_engine; import os; engine=create_engine(os.environ['DATABASE_URL']); conn=engine.connect(); conn.close()"; do
    echo "Database is not ready yet. Retrying in 2 seconds..."
    sleep 2
  done
fi

echo "Running database migrations..."
alembic upgrade head

echo "Starting FastAPI server..."
exec uvicorn src.app.main:app --host 0.0.0.0 --port "${PORT:-8000}"
