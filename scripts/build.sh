#!/bin/bash

set -e

# Configuration
IMAGE_NAME="ephemeral-backend"
IMAGE_TAG="${1:-latest}"
REGISTRY="${REGISTRY:-localhost:5000}"

echo "🔨 Building ephemeral backend..."

# Build the Docker image
echo "Building Docker image: ${IMAGE_NAME}:${IMAGE_TAG}"
docker build -t ${IMAGE_NAME}:${IMAGE_TAG} .

# Tag for registry if specified
if [ "$REGISTRY" != "localhost:5000" ]; then
    echo "Tagging image for registry: ${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}"
    docker tag ${IMAGE_NAME}:${IMAGE_TAG} ${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}
fi

echo "✅ Build completed successfully!"
echo "Image: ${IMAGE_NAME}:${IMAGE_TAG}"

# Optional: Run a quick test
echo "🧪 Running quick health check..."
CONTAINER_ID=$(docker run -d -p 8001:8000 ${IMAGE_NAME}:${IMAGE_TAG})

# Wait for container to start
sleep 5

# Test health endpoint
if curl -f http://localhost:8001/health > /dev/null 2>&1; then
    echo "✅ Health check passed!"
else
    echo "❌ Health check failed!"
    docker logs $CONTAINER_ID
    exit 1
fi

# Cleanup
docker stop $CONTAINER_ID > /dev/null
docker rm $CONTAINER_ID > /dev/null

echo "🚀 Ready for deployment!"