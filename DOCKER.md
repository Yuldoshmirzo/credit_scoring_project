# Docker & Containerization Guide

This project includes Docker support for containerized deployment and local development.

## Quick Start

### Build & Run with Docker Compose

```bash
# Build the image
docker-compose build

# Start all services
docker-compose up -d

# View running containers
docker-compose ps

# Access services:
# - MLflow UI: http://localhost:5000
# - FastAPI: http://localhost:8000
# - Main container: docker-compose exec credit-scoring bash
```

### Manual Docker Commands

```bash
# Build image
docker build -t credit-scoring:latest .

# Run container interactively
docker run -it -v $(pwd):/app credit-scoring:latest bash

# Run container with artifacts volume
docker run -it \
  -v $(pwd):/app \
  -v $(pwd)/artifacts:/app/artifacts \
  -v $(pwd)/data:/app/data \
  credit-scoring:latest bash

# Run MLflow UI
docker run -d -p 5000:5000 \
  -v $(pwd)/mlruns:/app/mlruns \
  credit-scoring:latest \
  mlflow ui --host 0.0.0.0 --port 5000

# Run FastAPI
docker run -d -p 8000:8000 \
  -v $(pwd):/app \
  credit-scoring:latest \
  uvicorn Api.main:app --host 0.0.0.0 --port 8000 --reload
```

## Services in docker-compose.yml

### 1. credit-scoring (Main Development Container)
- Interactive shell for running training/evaluation
- Mounts all project directories
- Volumes: code, artifacts, data, mlruns

### 2. mlflow (MLflow Tracking Server)
- Runs MLflow UI on port 5000
- Exposes experiment tracking and model registry
- Volume: mlruns/, mlartifacts/

### 3. api (FastAPI Server)
- Serves credit scoring API on port 8000
- Automatic reload on code changes
- Volume: code, artifacts

## Development Workflow

```bash
# Terminal 1: Start services
docker-compose up -d

# Terminal 2: Run training in main container
docker-compose exec credit-scoring python src/models/train.py

# Terminal 3: View MLflow
# Open http://localhost:5000

# Terminal 4: Test API
# Open http://localhost:8000/docs (Swagger UI)
```

## Production Deployment

### Push to Registry

```bash
# Build with version tag
docker build -t myregistry/credit-scoring:1.0.0 .

# Push to Docker Hub or private registry
docker push myregistry/credit-scoring:1.0.0

# Or with docker-compose
docker-compose config | docker-compose -f - push
```

### Run in Production

```bash
# Pull image
docker pull myregistry/credit-scoring:1.0.0

# Run with environment variables
docker run -d \
  -p 8000:8000 \
  -e ENV=production \
  -v /data/models:/app/artifacts \
  -v /data/input:/app/data \
  myregistry/credit-scoring:1.0.0 \
  uvicorn Api.main:app --host 0.0.0.0 --port 8000
```

## Dockerfile Details

- **Base**: Python 3.13 slim (minimal size)
- **Dependencies**: System packages (git, build-essential) + Python packages from requirements.txt
- **Ports**: 5000 (MLflow), 8000 (API)
- **Volumes**: Optimized for development and production

## Troubleshooting

```bash
# Check container logs
docker-compose logs credit-scoring
docker-compose logs mlflow
docker-compose logs api

# Debug container
docker-compose exec credit-scoring bash

# Rebuild without cache
docker-compose build --no-cache

# Stop all services
docker-compose down

# Remove dangling images
docker image prune -f

# Check image size
docker images credit-scoring

# Inspect container
docker inspect <container-id>
```

## .dockerignore

The Dockerfile automatically ignores:
- `.git/`, `.gitignore`
- `venv/`, `scoringenv/`
- `__pycache__/`, `*.pyc`
- `.pytest_cache/`, `.coverage`
- `mlruns/` (created inside container)
- `.vscode/`, `.idea/`

## Environment Variables (In Production)

```bash
PYTHONUNBUFFERED=1      # Unbuffered Python output
ENV=production          # Environment flag
MODEL_PATH=/app/artifacts/ensemble_model.pkl
DATA_PATH=/app/data/UCI_Credit_Card.csv
```

## Health Checks

Add to docker-compose.yml for production:

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s
```
