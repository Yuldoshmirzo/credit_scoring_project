# GitHub Setup & Data Versioning Guide

## Prerequisites

- GitHub account with Git installed
- Docker & Docker Compose installed
- DVC installed: `pip install dvc`

## 1. Initialize Git Repository

```bash
cd /path/to/credit_scoring_project

# Initialize git (if not already done)
git init

# Add all project files
git add .

# Make initial commit
git commit -m "Initial commit: Credit scoring ML pipeline with DVC setup"

# Add remote repository
git remote add origin https://github.com/YOUR_USERNAME/credit_scoring_project.git

# Push to GitHub
git branch -M main
git push -u origin main
```

## 2. Setup DVC for Data Versioning

### Local Storage (Development)

```bash
# Initialize DVC
dvc init

# Add local remote storage
mkdir -p ~/dvc-storage
dvc remote add -d local ~/dvc-storage

# Track data file
dvc add data/UCI_Credit_Card.csv

# Commit DVC files to git
git add data/UCI_Credit_Card.csv.dvc data/.gitignore
git commit -m "Track dataset with DVC"

# Push data to DVC remote
dvc push
```

### Cloud Storage (AWS S3 - Production)

```bash
# Create S3 bucket (AWS CLI required)
aws s3 mb s3://credit-scoring-dvc-storage

# Configure DVC remote
dvc remote add -d s3remote s3://credit-scoring-dvc-storage
dvc remote modify s3remote region us-east-1

# Configure AWS credentials (already configured in ~/.aws/credentials)
dvc remote modify s3remote profile default

# Track and push data
dvc add data/UCI_Credit_Card.csv
dvc push
```

### Google Cloud Storage

```bash
# Create GCS bucket
gsutil mb gs://credit-scoring-dvc-storage

# Configure DVC remote
dvc remote add -d gcs gs://credit-scoring-dvc-storage

# Authenticate with Google Cloud
gcloud auth application-default login

# Track and push data
dvc add data/UCI_Credit_Card.csv
dvc push
```

## 3. GitHub Secrets for CI/CD

Add these secrets to GitHub (Settings → Secrets → New repository secret):

- `DVC_REMOTE_PATH`: Path/URL to DVC remote storage
- `AWS_ACCESS_KEY_ID`: AWS credentials (if using S3)
- `AWS_SECRET_ACCESS_KEY`: AWS credentials (if using S3)
- `DOCKER_USERNAME`: Docker Hub username (for image push)
- `DOCKER_PASSWORD`: Docker Hub password/token

## 4. Docker Image Registry

### Push to Docker Hub

```bash
# Login to Docker Hub
docker login

# Build image
docker build -t yourname/credit-scoring:1.0.0 .

# Tag for Docker Hub
docker tag credit-scoring:latest yourname/credit-scoring:latest

# Push
docker push yourname/credit-scoring:1.0.0
docker push yourname/credit-scoring:latest
```

### GitHub Container Registry

```bash
# Login to GHCR
echo $GITHUB_TOKEN | docker login ghcr.io -u YOUR_USERNAME --password-stdin

# Build and tag
docker build -t ghcr.io/YOUR_USERNAME/credit-scoring:1.0.0 .

# Push
docker push ghcr.io/YOUR_USERNAME/credit-scoring:1.0.0
```

## 5. GitHub Actions Workflows

The project includes automated CI/CD workflows in `.github/workflows/`:

- **data-versioning.yml**: Validates data integrity and version control
- Add model training workflow: Create `.github/workflows/training.yml`

### Example Training Workflow

```yaml
name: Model Training

on:
  push:
    branches: [main]
    paths:
      - 'src/**'
      - 'requirements.txt'

jobs:
  train:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.13'
      
      - name: Install dependencies
        run: pip install -r requirements.txt
      
      - name: Pull data with DVC
        run: |
          dvc remote add -d local /tmp/dvc-storage
          dvc pull
      
      - name: Run training
        run: python src/models/train.py
      
      - name: Upload artifacts
        uses: actions/upload-artifact@v3
        with:
          name: ensemble-model
          path: artifacts/ensemble_model.pkl
```

## 6. Repository Structure for GitHub

```
credit_scoring_project/
├── .github/
│   ├── workflows/
│   │   ├── data-versioning.yml
│   │   └── training.yml
│   └── copilot-instructions.md
├── .dvcignore
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── DVC_SETUP.md
├── DOCKER.md
├── README.md
├── requirements.txt
├── src/
├── data/
│   └── UCI_Credit_Card.csv.dvc  ← DVC tracked
├── tests/
└── Api/
```

## 7. Collaboration Workflow

### For Developers

```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/credit_scoring_project.git
cd credit_scoring_project

# Setup environment
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Install DVC
dvc install

# Pull data
dvc pull

# Now you have all code, data, and dependencies
```

### Push Updates

```bash
# Make changes to code or data
# Update data
dvc add data/UCI_Credit_Card.csv

# Commit changes
git add -A
git commit -m "Update dataset and model"

# Push code to GitHub
git push origin main

# Push data to DVC remote
dvc push
```

## 8. Best Practices

✅ **Do:**
- Keep `.dvc` files in Git (small files)
- Store actual data in DVC remote (S3, GCS)
- Use `.gitignore` to exclude virtual environments
- Version Docker images with semantic versioning
- Document breaking changes in CHANGELOG.md

❌ **Don't:**
- Commit large data files directly to Git
- Store credentials in code or Git
- Push untagged Docker images to production
- Ignore CI/CD pipeline failures

## 9. Monitoring & Logging

```bash
# View DVC status
dvc status

# Check Git status
git status

# View DVC configuration
dvc config -l

# List all tracked files
dvc list -R .
```

## 10. Troubleshooting

```bash
# DVC not finding data
dvc status --check

# Reset local cache
dvc gc -w

# Reinitialize DVC
dvc destroy && dvc init

# Force pull latest data
dvc pull --force

# Debug GitHub Actions locally
act -j train  # Requires act tool: https://github.com/nektos/act
```
