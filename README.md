# Ephemeral Backend

A modern, scalable, and stateless backend API designed for Kubernetes with built-in observability, security, and auto-scaling capabilities.

## 🚀 Features

- **FastAPI Framework**: High-performance async API with automatic OpenAPI documentation
- **Kubernetes-Native**: Optimized for ephemeral, stateless deployments
- **Auto-Scaling**: Horizontal Pod Autoscaler with CPU and memory metrics
- **Observability**: Prometheus metrics, structured logging, and health checks
- **Security**: Non-root containers, network policies, and security contexts
- **Production-Ready**: Multi-stage Docker builds, graceful shutdowns, and resource limits

## 📋 Prerequisites

- **Docker** (20.10+)
- **Kubernetes** (1.21+)
- **kubectl** configured for your cluster
- **Optional**: Prometheus Operator for monitoring

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│     Ingress     │    │   Service       │    │  Deployment     │
│  (Load Balancer)│───▶│ (ClusterIP)     │───▶│   (3 replicas)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                       │
┌─────────────────┐    ┌─────────────────┐            │
│       HPA       │    │  NetworkPolicy  │            │
│  (Auto-scaling) │    │   (Security)    │            │
└─────────────────┘    └─────────────────┘            │
                                                       │
┌─────────────────┐    ┌─────────────────┐            │
│   Prometheus    │    │   ConfigMap     │            │
│  (Monitoring)   │───▶│ (Configuration) │◀───────────┘
└─────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### Local Development

1. **Clone and setup**:
   ```bash
   git clone <repository>
   cd ephemeral-backend
   ```

2. **Start development server**:
   ```bash
   chmod +x scripts/dev.sh
   ./scripts/dev.sh
   ```

3. **Access the API**:
   - API Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health
   - Metrics: http://localhost:8000/metrics

### Production Deployment

1. **Build the image**:
   ```bash
   chmod +x scripts/build.sh
   ./scripts/build.sh v1.0.0
   ```

2. **Deploy to Kubernetes**:
   ```bash
   chmod +x scripts/deploy.sh
   ./scripts/deploy.sh v1.0.0
   ```

## 📁 Project Structure

```
ephemeral-backend/
├── app/
│   └── main.py              # FastAPI application
├── k8s/                     # Kubernetes manifests
│   ├── namespace.yaml       # Namespace definition
│   ├── configmap.yaml       # Configuration
│   ├── deployment.yaml      # Main deployment
│   ├── service.yaml         # Service definition
│   ├── hpa.yaml            # Auto-scaling configuration
│   ├── ingress.yaml        # External access
│   └── network-policy.yaml # Security policies
├── monitoring/              # Observability
│   ├── servicemonitor.yaml # Prometheus scraping
│   └── prometheusrule.yaml # Alerting rules
├── scripts/                 # Utility scripts
│   ├── build.sh            # Container build script
│   ├── deploy.sh           # Deployment script
│   └── dev.sh              # Development server
├── Dockerfile              # Multi-stage container build
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## 🔧 Configuration

### Environment Variables

| Variable      | Default       | Description                    |
|---------------|---------------|--------------------------------|
| `PORT`        | `8000`        | Server port                    |
| `ENVIRONMENT` | `development` | Environment (dev/staging/prod) |
| `LOG_LEVEL`   | `info`        | Logging level                  |

### Kubernetes Configuration

Modify `k8s/configmap.yaml` to adjust application settings:

```yaml
data:
  ENVIRONMENT: "production"
  LOG_LEVEL: "info"
  PORT: "8000"
```

## 📊 API Endpoints

### Core Endpoints

- `GET /` - API information
- `GET /health` - Health check (for load balancers)
- `GET /health/ready` - Readiness probe (for Kubernetes)
- `GET /health/live` - Liveness probe (for Kubernetes)
- `GET /metrics` - Prometheus metrics

### Task Management (Demo)

- `POST /tasks` - Create a new task
- `GET /tasks/{task_id}` - Get task status
- `GET /tasks` - List all tasks
- `DELETE /tasks/{task_id}` - Delete a task

### Example Usage

```bash
# Create a task
curl -X POST "http://localhost:8000/tasks" \
  -H "Content-Type: application/json" \
  -d '{
    "task_id": "task-123",
    "data": {"message": "Hello World"},
    "priority": 1
  }'

# Check task status
curl "http://localhost:8000/tasks/task-123"

# List all tasks
curl "http://localhost:8000/tasks"
```

## 🔍 Monitoring & Observability

### Metrics

The application exposes Prometheus metrics at `/metrics`:

- `http_requests_total` - Total HTTP requests by method, endpoint, and status
- `http_request_duration_seconds` - HTTP request duration histogram

### Health Checks

- **Liveness**: `/health/live` - Indicates if the app is running
- **Readiness**: `/health/ready` - Indicates if the app can serve traffic

### Alerts

Pre-configured Prometheus alerts:

- Service down detection
- High CPU/memory usage
- High error rates
- Slow response times

## 🛡️ Security Features

- **Non-root containers**: Runs as user `1001`
- **Read-only root filesystem**: Prevents runtime modifications
- **Security contexts**: Drops all Linux capabilities
- **Network policies**: Restricts ingress/egress traffic
- **Resource limits**: Prevents resource exhaustion

## 📈 Auto-Scaling

The HPA (Horizontal Pod Autoscaler) automatically scales based on:

- **CPU utilization**: Target 70%
- **Memory utilization**: Target 80%
- **Replica range**: 2-10 pods

Scaling behavior:
- **Scale up**: Aggressive (100% increase every 15s)
- **Scale down**: Conservative (50% decrease every 60s, 5min stabilization)

## 🚀 Deployment Options

### Local Kubernetes (minikube/kind)

```bash
# Start minikube
minikube start

# Build and deploy
./scripts/build.sh
./scripts/deploy.sh

# Access via port-forward
kubectl port-forward svc/ephemeral-backend-service 8080:80 -n ephemeral-backend
```

### Cloud Kubernetes (GKE/EKS/AKS)

```bash
# Set your registry
export REGISTRY=your-registry.com

# Build and push
./scripts/build.sh v1.0.0
docker push $REGISTRY/ephemeral-backend:v1.0.0

# Update deployment image
sed -i 's|ephemeral-backend:latest|'$REGISTRY'/ephemeral-backend:v1.0.0|' k8s/deployment.yaml

# Deploy
./scripts/deploy.sh v1.0.0
```

## 🔧 Development

### Adding New Endpoints

1. Add your endpoint to `app/main.py`
2. Update the Pydantic models if needed
3. Test locally with `./scripts/dev.sh`
4. Build and deploy: `./scripts/build.sh && ./scripts/deploy.sh`

### Customizing for Your Use Case

This backend is designed as a template. Customize it by:

1. **Replace the task endpoints** with your business logic
2. **Add external service integrations** (databases, APIs, etc.)
3. **Update health checks** to verify your dependencies
4. **Modify resource limits** based on your workload
5. **Adjust auto-scaling metrics** for your traffic patterns

## 🐛 Troubleshooting

### Common Issues

1. **Pod crashes or restarts**:
   ```bash
   kubectl logs -f deployment/ephemeral-backend -n ephemeral-backend
   kubectl describe pod <pod-name> -n ephemeral-backend
   ```

2. **Service not accessible**:
   ```bash
   kubectl get svc -n ephemeral-backend
   kubectl describe ingress -n ephemeral-backend
   ```

3. **Auto-scaling not working**:
   ```bash
   kubectl describe hpa ephemeral-backend-hpa -n ephemeral-backend
   kubectl top pods -n ephemeral-backend
   ```

### Debug Commands

```bash
# Get pod logs
kubectl logs -f deployment/ephemeral-backend -n ephemeral-backend

# Shell into a pod
kubectl exec -it deployment/ephemeral-backend -n ephemeral-backend -- /bin/bash

# Check resource usage
kubectl top pods -n ephemeral-backend

# View events
kubectl get events -n ephemeral-backend --sort-by='.lastTimestamp'
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) for the excellent web framework
- [Kubernetes](https://kubernetes.io/) for the orchestration platform
- [Prometheus](https://prometheus.io/) for monitoring and alerting