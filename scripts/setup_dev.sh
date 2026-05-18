#!/bin/bash

# CourseFlow Local Development Setup
# ===================================

echo "CourseFlow API - Development Environment Setup"
echo "================================================"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 not found. Please install Python 3.11+"
    exit 1
fi

echo "✓ Python $(python3 --version) found"

# Create virtual environment if not exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate venv
source venv/bin/activate
echo "✓ Virtual environment activated"

# Install dependencies
echo "Installing dependencies..."
pip install -q -r requirements.txt
echo "✓ Dependencies installed"

# Initialize database
echo "Initializing SQLite database..."
python3 << 'PYEOF'
import sys
sys.path.insert(0, '/Users/mirelvolcan/CourseFlow')

from sqlalchemy import create_engine
from app.db.base import Base

# Create engine with SQLite
engine = create_engine("sqlite:///courseflow.db")

# Create all tables
Base.metadata.create_all(bind=engine)
print("✓ Database initialized with all tables")
PYEOF

# Summary
echo ""
echo "Setup complete!"
echo ""
echo "To start the API server, run:"
echo "  source venv/bin/activate"
echo "  uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo "API will be available at: http://localhost:8000"
echo "API Docs (Swagger): http://localhost:8000/docs"
echo ""
