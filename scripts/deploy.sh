#!/bin/bash

set -e

# Configuration
NAMESPACE="ephemeral-backend"
IMAGE_TAG="${1:-latest}"
KUBECTL_CONTEXT="${KUBECTL_CONTEXT:-}"

echo "🚀 Deploying ephemeral backend to Kubernetes..."

# Set kubectl context if specified
if [ -n "$KUBECTL_CONTEXT" ]; then
    echo "Using kubectl context: $KUBECTL_CONTEXT"
    kubectl config use-context $KUBECTL_CONTEXT
fi

# Create namespace if it doesn't exist
echo "Creating namespace: $NAMESPACE"
kubectl apply -f k8s/namespace.yaml

# Apply ConfigMap
echo "Applying ConfigMap..."
kubectl apply -f k8s/configmap.yaml

# Apply NetworkPolicy (if supported)
echo "Applying NetworkPolicy..."
kubectl apply -f k8s/network-policy.yaml || echo "⚠️  NetworkPolicy not supported, skipping..."

# Update deployment image tag
echo "Updating deployment with image tag: $IMAGE_TAG"
sed "s|image: ephemeral-backend:latest|image: ephemeral-backend:$IMAGE_TAG|g" k8s/deployment.yaml | kubectl apply -f -

# Apply service
echo "Applying Service..."
kubectl apply -f k8s/service.yaml

# Apply HPA
echo "Applying HorizontalPodAutoscaler..."
kubectl apply -f k8s/hpa.yaml

# Apply Ingress (optional)
echo "Applying Ingress..."
kubectl apply -f k8s/ingress.yaml || echo "⚠️  Ingress not configured or not supported, skipping..."

# Apply monitoring (if Prometheus operator is available)
echo "Applying monitoring configuration..."
kubectl apply -f monitoring/ || echo "⚠️  Prometheus operator not available, skipping monitoring..."

# Wait for deployment to be ready
echo "⏳ Waiting for deployment to be ready..."
kubectl wait --for=condition=available --timeout=300s deployment/ephemeral-backend -n $NAMESPACE

# Get deployment status
echo "📊 Deployment status:"
kubectl get pods -n $NAMESPACE -l app=ephemeral-backend
kubectl get svc -n $NAMESPACE
kubectl get hpa -n $NAMESPACE

# Get service endpoint
SERVICE_IP=$(kubectl get svc ephemeral-backend-service -n $NAMESPACE -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "ClusterIP")
SERVICE_PORT=$(kubectl get svc ephemeral-backend-service -n $NAMESPACE -o jsonpath='{.spec.ports[0].port}')

echo ""
echo "✅ Deployment completed successfully!"
echo "📡 Service endpoint: $SERVICE_IP:$SERVICE_PORT"
echo "🔍 Health check: curl http://$SERVICE_IP:$SERVICE_PORT/health"
echo "📖 API docs: http://$SERVICE_IP:$SERVICE_PORT/docs"
echo ""
echo "🔧 Useful commands:"
echo "  kubectl get pods -n $NAMESPACE"
echo "  kubectl logs -f deployment/ephemeral-backend -n $NAMESPACE"
echo "  kubectl describe hpa ephemeral-backend-hpa -n $NAMESPACE"