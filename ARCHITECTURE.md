

```
┌─────────────────────────────────────────────────────────────────┐
│                     Credit Scoring ML Pipeline                   │
└─────────────────────────────────────────────────────────────────┘

                            GitHub Repository
                                   │
                    ┌──────────────┼──────────────┐
                    │              │              │
                    ▼              ▼              ▼
              Source Code      DVC Files       Workflows
                    │         (*.dvc)      (.github/workflows/)
                    │              │              │
                    └──────────────┼──────────────┘
                                   │
                    ┌──────────────┼──────────────┐
                    │              │              │
                    ▼              ▼              ▼
                Docker       DVC Remote        CI/CD
              (Dockerfile)    Storage          Pipeline
                    │        (S3/GCS)         (GitHub Actions)
                    │         (Local)                │
                    │              │                 │
                    └──────────────┼─────────────────┘
                                   │
                    ┌──────────────┼──────────────┐
                    │              │              │
                    ▼              ▼              ▼
            Development    Production      Testing &
            (docker-compose)  (Kubernetes)  Validation
```

## Docker Service Architecture

```
docker-compose.yml
│
├── credit-scoring (Main Service)
│   ├── Volumes: /app (code), /data, /artifacts
│   ├── Mounts: Current project directory
│   └── Purpose: Training, evaluation, development
│
├── mlflow (Tracking Server)
│   ├── Volumes: /mlruns, /mlartifacts
│   ├── Port: 5000 (HTTP)
│   └── Purpose: Experiment tracking & model registry
│
└── api (FastAPI Server)
    ├── Volumes: /app (code), /artifacts
    ├── Port: 8000 (HTTP)
    ├── Depends On: credit-scoring service
    └── Purpose: Real-time inference API
```

## Data Flow with DVC

```
┌─────────────────────────┐
│   UCI_Credit_Card.csv   │  Raw Data (22MB)
└────────────┬────────────┘
             │
             ▼
     ┌───────────────┐
     │  dvc add      │
     └───────┬───────┘
             │
     ┌───────▼───────────────────┐
     │ UCI_Credit_Card.csv.dvc   │  Metadata File (small)
     │   ├─ path: ...            │
     │   ├─ md5: ...             │
     │   └─ sizes: ...           │
     └───────┬───────────────────┘
             │
     ┌───────▼──────────────────┐
     │   Git (.gitignore)       │
     │   ✓ Tracks .dvc file     │
     │   ✗ Ignores raw CSV      │
     └───────┬──────────────────┘
             │
     ┌───────▼──────────────────┐
     │   GitHub Repository      │
     │   - Code                 │
     │   - .dvc files           │
     │   - Documentation        │
     └───────┬──────────────────┘
             │
     ┌───────▼──────────────────┐
     │   DVC Remote Storage     │
     │   ├─ Local: ~/dvc-stor   │
     │   ├─ S3: s3://bucket     │
     │   └─ GCS: gs://bucket    │
     └─────────────────────────┘
```

## Deployment Scenarios

### Scenario 1: Local Development

```
Developer Machine
│
├─ Git Clone
│  └─ .dvc files, code, requirements.txt
│
├─ dvc pull
│  └─ Downloads UCI_Credit_Card.csv from DVC remote
│
├─ pip install -r requirements.txt
│  └─ Installs dependencies
│
├─ jupyter notebook evaluate.ipynb
│  └─ Trains model, logs to MLflow
│
└─ uvicorn Api.main:app
   └─ Serves predictions on http://localhost:8000
```

### Scenario 2: Docker Development

```
Docker Host
│
├─ docker-compose up -d
│  │
│  ├─ credit-scoring container
│  │  └─ Volume mounts: current directory
│  │
│  ├─ mlflow container
│  │  └─ MLflow UI: http://localhost:5000
│  │
│  └─ api container
│     └─ FastAPI: http://localhost:8000
│
└─ Update code/data → Changes reflected immediately
```

### Scenario 3: Production - AWS ECS

```
GitHub (push code + data)
  │
  ├─ Trigger GitHub Actions
  │  └─ Run tests, validate data
  │
  └─ Build Docker image
     └─ Push to ECR (Elastic Container Registry)
        │
        ├─ ECS Task Definition
        │  ├─ Container: credit-scoring-api:latest
        │  ├─ Port: 8000
        │  ├─ Environment: MODEL_PATH, DATA_PATH
        │  └─ Volume: EFS (for artifacts)
        │
        └─ ECS Service
           ├─ Load Balancer (distribute traffic)
           ├─ Auto Scaling (scale based on metrics)
           └─ CloudWatch (monitor logs & metrics)

External Users
  └─ POST /predict
     └─ Response: {probability, prediction}
```

### Scenario 4: Production - Kubernetes

```
GitHub (push)
  │
  └─ Trigger Tekton/ArgoCD Pipeline
     │
     ├─ Build image
     ├─ Push to container registry
     └─ Deploy to Kubernetes
        │
        ├─ Deployment: api-server
        │  ├─ Replicas: 3
        │  ├─ Image: myregistry/credit-scoring:1.0.0
        │  └─ Resources: CPU, Memory limits
        │
        ├─ Service: api-service
        │  ├─ Type: LoadBalancer
        │  ├─ Port: 8000
        │  └─ Selector: app=credit-scoring
        │
        ├─ ConfigMap: model-config
        │  ├─ MODEL_PATH
        │  └─ PREDICTION_THRESHOLD
        │
        └─ PersistentVolumeClaim: model-storage
           └─ Mount: ensemble_model.pkl
```

## CI/CD Pipeline Flow

```
┌─────────────────────────────────────────────────────────┐
│            GitHub Push / Pull Request                    │
└────────────┬────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────┐
│         GitHub Actions Workflow Triggered                │
│  (.github/workflows/data-versioning.yml)                 │
└────────────┬────────────────────────────────────────────┘
             │
     ┌───────┴────────┬──────────────┬──────────────┐
     │                │              │              │
     ▼                ▼              ▼              ▼
┌──────────┐   ┌────────────┐  ┌──────────┐  ┌──────────┐
│ Setup    │   │ Pull Data  │  │ Run      │  │ Validate │
│ Python   │   │ with DVC   │  │ Tests    │  │ Artifacts│
└────┬─────┘   └────┬───────┘  └────┬─────┘  └────┬─────┘
     │              │               │             │
     └──────────────┴───────────────┴─────────────┘
                      │
     ┌────────────────▼────────────────┐
     │  All Checks Passed?              │
     └────┬─────────────────────────┬───┘
          │ YES                     │ NO
          ▼                         ▼
    ┌──────────────┐         ┌──────────────┐
    │ Mark as OK   │         │ Fail & Alert │
    └──────┬───────┘         └──────────────┘
           │
           ▼
    ┌──────────────────────────┐
    │ Merge to main (optional) │
    └──────┬───────────────────┘
           │
           ▼
    ┌──────────────────────────┐
    │ Build Docker Image       │
    └──────┬───────────────────┘
           │
           ▼
    ┌──────────────────────────┐
    │ Push to Registry         │
    └──────┬───────────────────┘
           │
           ▼
    ┌──────────────────────────┐
    │ Deploy to Production     │
    │ (if approved)            │
    └──────────────────────────┘
```

## Security Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   Security Layers                       │
└─────────────────────────────────────────────────────────┘

├─ Git Level
│  ├─ .gitignore prevents credential commits
│  ├─ .dvc files track large files (not credentials)
│  └─ Code review before merge
│
├─ GitHub Level
│  ├─ GitHub Secrets for credentials
│  ├─ Branch protection rules
│  ├─ Action-only secrets (not exposed in logs)
│  └─ OAuth tokens with limited scope
│
├─ Docker Level
│  ├─ Non-root user in container
│  ├─ Read-only filesystems where possible
│  ├─ No credentials in Dockerfile
│  └─ Minimal base image (slim variant)
│
├─ Application Level
│  ├─ Environment variables for secrets
│  ├─ FastAPI CORS configuration
│  ├─ Input validation (Pydantic)
│  └─ Rate limiting on API endpoints
│
└─ Infrastructure Level
   ├─ TLS/HTTPS for API communication
   ├─ IAM roles for cloud services
   ├─ Network policies (VPC, security groups)
   └─ Audit logging for all actions
```

## Monitoring & Observability

```
Application
│
├─ Logs
│  ├─ Application logs → CloudWatch / ELK
│  ├─ MLflow logs → mlruns/
│  └─ Docker logs → docker logs command
│
├─ Metrics
│  ├─ Model metrics → MLflow UI
│  ├─ API metrics → Prometheus
│  ├─ Resource usage → CloudWatch / Datadog
│  └─ Data quality → Great Expectations
│
└─ Alerting
   ├─ Model performance drop → Slack/Email
   ├─ API latency threshold → PagerDuty
   ├─ Data validation failures → GitHub Issues
   └─ Docker service crashes → Health checks
```

## Update & Rollback Process

```
┌─────────────────────────────────────────────────────────┐
│              Release Process (Main Branch)               │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
              ┌─────────────┐
              │ Git Tag     │  v1.0.0
              │ Release     │
              └────┬────────┘
                   │
         ┌─────────┴─────────┐
         │                   │
         ▼                   ▼
    ┌─────────┐         ┌──────────┐
    │ Staging │◄────────┤Production│
    │Canary   │         │Full      │
    └─────────┘         └──────────┘
         │
    Deploy to
    10% traffic
         │
    Monitor metrics
         │
    If OK: 100% traffic
    If BAD: Rollback
```

## File Organization

```
.
├── Code Version Control (Git)
│   ├── .git/
│   ├── .github/workflows/
│   ├── .gitignore
│   └── src/, tests/, Api/
│
├── Data Version Control (DVC)
│   ├── .dvc/
│   ├── .dvcignore
│   ├── data/UCI_Credit_Card.csv.dvc
│   └── artifacts/ensemble_model.pkl.dvc (optional)
│
├── Containerization (Docker)
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── .dockerignore
│
└── Documentation
    ├── README.md
    ├── DVC_SETUP.md
    ├── DOCKER.md
    ├── GITHUB_SETUP.md
    └── ARCHITECTURE.md (this file)
```

---

**This architecture supports:**
✓ Local development with hot-reload  
✓ Reproducible environments with Docker  
✓ Data versioning & collaboration with DVC  
✓ Automated testing & deployment with GitHub Actions  
✓ Scalable production deployments on cloud platforms
