#!/usr/bin/env bash
# QUICK REFERENCE - Copy/paste commands

# ============================================================================
# 🚀 QUICK START
# ============================================================================

# 1. SETUP DVC & GIT (One-liner)
chmod +x setup-github-dvc.sh && ./setup-github-dvc.sh

# 2. OR MANUAL SETUP
dvc init
dvc remote add -d local ~/dvc-storage
dvc add data/UCI_Credit_Card.csv
git add data/*.dvc data/.gitignore .dvc .dvcignore .gitignore
git commit -m "Initial commit with DVC setup"

# ============================================================================
# 📦 DOCKER COMMANDS
# ============================================================================

# Start all services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f

# Run command in container
docker-compose exec credit-scoring python src/models/train.py

# Build fresh image
docker-compose build --no-cache

# Push to Docker Hub
docker login
docker tag credit-scoring:latest username/credit-scoring:latest
docker push username/credit-scoring:latest

# ============================================================================
# 📊 DVC COMMANDS
# ============================================================================

# Initialize DVC
dvc init

# Add file to DVC
dvc add data/UCI_Credit_Card.csv

# Pull data from remote
dvc pull

# Push data to remote
dvc push

# Check status
dvc status

# Configure local remote
dvc remote add -d local ~/dvc-storage

# Configure S3 remote
dvc remote add -d s3 s3://bucket-name
dvc remote modify s3 region us-east-1

# List all remotes
dvc remote list

# ============================================================================
# 🔗 GIT COMMANDS
# ============================================================================

# Initialize git
git init

# Add all files
git add -A

# Commit
git commit -m "Your message"

# Add GitHub remote
git remote add origin https://github.com/USERNAME/credit_scoring_project.git

# Push to GitHub
git branch -M main
git push -u origin main

# Undo last commit
git reset --soft HEAD~1

# View commit history
git log --oneline -10

# ============================================================================
# 🧪 TESTING & VALIDATION
# ============================================================================

# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_model.py -v

# Run tests with coverage
pytest tests/ --cov=src --cov-report=html

# Check Python syntax
python -m py_compile src/models/train.py

# ============================================================================
# 🔍 VERIFICATION COMMANDS
# ============================================================================

# Check data file exists
ls -lh data/UCI_Credit_Card.csv

# Check model exists
ls -lh artifacts/ensemble_model.pkl

# Check DVC is tracking file
cat data/UCI_Credit_Card.csv.dvc

# Verify Git remote
git remote -v

# List Docker images
docker images

# Check container status
docker ps -a

# ============================================================================
# 🐛 TROUBLESHOOTING
# ============================================================================

# Clear Docker system
docker system prune -a

# Remove DVC cache
dvc gc -w

# Reset DVC
dvc destroy && dvc init

# Force pull latest data
dvc pull --force

# Check port is available
lsof -i :5000  # MLflow
lsof -i :8000  # API

# Kill process on port
kill -9 $(lsof -t -i:5000)

# View Docker build output
docker build -t credit-scoring:test . --progress=plain

# ============================================================================
# 💾 GITHUB WORKFLOW
# ============================================================================

# Create new branch
git checkout -b feature/new-feature

# Make changes, then:
git add .
git commit -m "Your message"

# Push branch
git push origin feature/new-feature

# Create Pull Request on GitHub (via browser)

# After review merged to main:
git checkout main
git pull origin main

# ============================================================================
# 📊 MLFLOW COMMANDS
# ============================================================================

# Start MLflow UI
mlflow ui

# View specific experiment
mlflow experiments search --names "credit_scoring_ensemble"

# Download best model
mlflow models download-artifacts -u runs://<RUN_ID> -d ./local_model

# ============================================================================
# 🚀 DEPLOYMENT
# ============================================================================

# AWS ECS (after setting up task definition)
aws ecs update-service --cluster credit-scoring --service api --force-new-deployment

# Kubernetes deploy
kubectl apply -f k8s/deployment.yaml

# Local testing
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"LIMIT_BAL": 20000, "AGE": 25}'

# ============================================================================
# 📝 FILE LOCATIONS
# ============================================================================

# Data file
data/UCI_Credit_Card.csv

# DVC tracking file
data/UCI_Credit_Card.csv.dvc

# Trained model
artifacts/ensemble_model.pkl

# MLflow experiments
mlruns/244209017549523150/

# Docker config
Dockerfile
docker-compose.yml

# Documentation
README.md
DOCKER.md
DVC_SETUP.md
GITHUB_SETUP.md
ARCHITECTURE.md

# ============================================================================
# 🎯 COMMON WORKFLOWS
# ============================================================================

# WORKFLOW 1: Update data
dvc add data/UCI_Credit_Card.csv
dvc push
git add data/UCI_Credit_Card.csv.dvc
git commit -m "Update dataset"
git push

# WORKFLOW 2: Train model locally
docker-compose up -d
docker-compose exec credit-scoring bash
jupyter notebook src/models/evaluate.ipynb
# (Train model, evaluate, log to MLflow)
dvc push

# WORKFLOW 3: Make prediction
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{...}'

# WORKFLOW 4: Deploy to production
git tag v1.0.0
git push origin v1.0.0
docker build -t myregistry/credit-scoring:1.0.0 .
docker push myregistry/credit-scoring:1.0.0
# Trigger deployment (ECS/K8s/etc)

# ============================================================================
# 💡 HELPFUL TIPS
# ============================================================================

# Alias for common commands
alias dcup='docker-compose up -d'
alias dcdown='docker-compose down'
alias dclogs='docker-compose logs -f'
alias gitpush='git add -A && git commit -m "Update" && git push'

# Environment variables
export PYTHONUNBUFFERED=1
export MODEL_PATH=/app/artifacts/ensemble_model.pkl
export DATA_PATH=/app/data/UCI_Credit_Card.csv

# ============================================================================

# Questions? Check documentation:
# README.md          - Project overview
# DOCKER.md          - Docker guide
# DVC_SETUP.md       - Data versioning
# GITHUB_SETUP.md    - GitHub integration
# ARCHITECTURE.md    - System design
# CHECKLIST.md       - Validation checklist

echo "✅ Reference saved!"
