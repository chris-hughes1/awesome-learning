import asyncio
import logging
import os
import time
from contextlib import asynccontextmanager
from typing import Dict, Any, Optional

import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from pydantic import BaseModel
import httpx

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Prometheus metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status_code'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration')

# Pydantic models
class HealthResponse(BaseModel):
    status: str
    timestamp: float
    version: str = "1.0.0"
    environment: str = os.getenv("ENVIRONMENT", "development")

class TaskRequest(BaseModel):
    task_id: str
    data: Dict[str, Any]
    priority: int = 1

class TaskResponse(BaseModel):
    task_id: str
    status: str
    message: str
    result: Optional[Dict[str, Any]] = None

# Global state for demo purposes (in production, use Redis or similar)
tasks_store: Dict[str, Dict] = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    logger.info("Starting up ephemeral backend...")
    # Startup logic here (connect to external services, etc.)
    yield
    logger.info("Shutting down ephemeral backend...")
    # Cleanup logic here

# Create FastAPI app
app = FastAPI(
    title="Ephemeral Backend API",
    description="A scalable, stateless backend designed for Kubernetes",
    version="1.0.0",
    lifespan=lifespan
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # Configure appropriately for production
)

@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    """Middleware to collect Prometheus metrics"""
    start_time = time.time()
    
    response = await call_next(request)
    
    duration = time.time() - start_time
    REQUEST_DURATION.observe(duration)
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        status_code=response.status_code
    ).inc()
    
    return response

# Health check endpoints
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint for Kubernetes probes"""
    return HealthResponse(
        status="healthy",
        timestamp=time.time()
    )

@app.get("/health/ready")
async def readiness_check():
    """Readiness check for Kubernetes"""
    # Add checks for external dependencies here
    try:
        # Example: check external service
        async with httpx.AsyncClient() as client:
            # Replace with actual dependency check
            pass
        return {"status": "ready", "timestamp": time.time()}
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        raise HTTPException(status_code=503, detail="Service not ready")

@app.get("/health/live")
async def liveness_check():
    """Liveness check for Kubernetes"""
    return {"status": "alive", "timestamp": time.time()}

# Metrics endpoint
@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return JSONResponse(
        content=generate_latest().decode("utf-8"),
        media_type=CONTENT_TYPE_LATEST
    )

# API endpoints
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Ephemeral Backend API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

@app.post("/tasks", response_model=TaskResponse)
async def create_task(task: TaskRequest, background_tasks: BackgroundTasks):
    """Create a new task (demo endpoint)"""
    logger.info(f"Creating task: {task.task_id}")
    
    # Store task (in production, use proper storage)
    tasks_store[task.task_id] = {
        "status": "pending",
        "data": task.data,
        "priority": task.priority,
        "created_at": time.time()
    }
    
    # Add background processing
    background_tasks.add_task(process_task, task.task_id)
    
    return TaskResponse(
        task_id=task.task_id,
        status="accepted",
        message="Task created successfully"
    )

@app.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task(task_id: str):
    """Get task status"""
    if task_id not in tasks_store:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task_data = tasks_store[task_id]
    return TaskResponse(
        task_id=task_id,
        status=task_data["status"],
        message="Task retrieved successfully",
        result=task_data.get("result")
    )

@app.delete("/tasks/{task_id}")
async def delete_task(task_id: str):
    """Delete a task"""
    if task_id not in tasks_store:
        raise HTTPException(status_code=404, detail="Task not found")
    
    del tasks_store[task_id]
    logger.info(f"Deleted task: {task_id}")
    return {"message": "Task deleted successfully"}

@app.get("/tasks")
async def list_tasks():
    """List all tasks"""
    return {
        "tasks": [
            {"task_id": tid, **data} 
            for tid, data in tasks_store.items()
        ],
        "count": len(tasks_store)
    }

async def process_task(task_id: str):
    """Background task processing"""
    logger.info(f"Processing task: {task_id}")
    
    # Simulate processing
    await asyncio.sleep(2)
    
    # Update task status
    if task_id in tasks_store:
        tasks_store[task_id]["status"] = "completed"
        tasks_store[task_id]["result"] = {
            "processed_at": time.time(),
            "message": "Task completed successfully"
        }
        logger.info(f"Task {task_id} completed")

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8000")),
        log_level="info"
    )