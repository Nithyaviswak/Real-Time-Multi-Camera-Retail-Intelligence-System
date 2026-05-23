#!/bin/bash
# Setup script for Retail Intelligence System

echo "========================================"
echo "Retail Intelligence System - Setup"
echo "========================================"

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $PYTHON_VERSION"

# Create necessary directories
echo "Creating directories..."
mkdir -p models
mkdir -p data/videos
mkdir -p data/configs

# Install backend dependencies
echo "Installing backend dependencies..."

echo "Installing stream-manager..."
pip install -q -r backend/stream-manager/requirements.txt 2>/dev/null || true

echo "Installing detection-service..."
pip install -q -r backend/detection-service/requirements.txt 2>/dev/null || true

echo "Installing tracking-service..."
pip install -q -r backend/tracking-service/requirements.txt 2>/dev/null || true

echo "Installing analytics-service..."
pip install -q -r backend/analytics-service/requirements.txt 2>/dev/null || true

echo "Installing alert-service..."
pip install -q -r backend/alert-service/requirements.txt 2>/dev/null || true

echo "Installing api-gateway..."
pip install -q -r backend/api-gateway/requirements.txt 2>/dev/null || true

# Install frontend dependencies
echo "Installing frontend dependencies..."
cd frontend/dashboard
npm install 2>/dev/null || true
cd ../..

echo ""
echo "========================================"
echo "Setup Complete!"
echo "========================================"
echo ""
echo "To run the demo:"
echo "  python scripts/demo.py --duration 30"
echo ""
echo "To start services with Docker:"
echo "  docker-compose up -d"
echo ""
echo "To access the dashboard:"
echo "  http://localhost:3000"
echo ""
