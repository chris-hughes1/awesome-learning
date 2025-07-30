#!/bin/bash

set -e

echo "🛠️  Starting development environment..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Check if requirements.txt exists
if [ ! -f "requirements.txt" ]; then
    echo "❌ requirements.txt not found. Run from project root."
    exit 1
fi

# Development configuration
DEV_PORT="${DEV_PORT:-8000}"
DEV_IMAGE="ephemeral-backend:dev"

echo "🔨 Building development image..."
docker build -t $DEV_IMAGE .

echo "🚀 Starting development server on port $DEV_PORT..."
echo "📖 API docs available at: http://localhost:$DEV_PORT/docs"
echo "🔍 Health check: http://localhost:$DEV_PORT/health"
echo "📊 Metrics: http://localhost:$DEV_PORT/metrics"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Run the container with development settings
docker run --rm -it \
    -p $DEV_PORT:8000 \
    -e ENVIRONMENT=development \
    -e LOG_LEVEL=debug \
    --name ephemeral-backend-dev \
    $DEV_IMAGE