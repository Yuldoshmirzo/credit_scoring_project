#!/bin/bash
# Quick setup script for GitHub + DVC integration

set -e  # Exit on error

echo "🚀 Credit Scoring Project - GitHub & DVC Setup"
echo "==============================================="

# 1. Initialize Git
echo "📦 Initializing Git repository..."
if [ ! -d ".git" ]; then
    git init
    echo "✓ Git initialized"
else
    echo "✓ Git already initialized"
fi

# 2. Initialize DVC
echo "📊 Initializing DVC..."
if [ ! -d ".dvc" ]; then
    dvc init
    echo "✓ DVC initialized"
else
    echo "✓ DVC already initialized"
fi

# 3. Configure DVC local remote
echo "💾 Setting up DVC storage..."
mkdir -p ~/dvc-storage
dvc remote add -d local ~/dvc-storage 2>/dev/null || dvc remote modify -d local ~/dvc-storage
echo "✓ DVC remote storage configured at ~/dvc-storage"

# 4. Track data with DVC
echo "📈 Tracking data files with DVC..."
if [ -f "data/UCI_Credit_Card.csv" ]; then
    dvc add data/UCI_Credit_Card.csv
    echo "✓ Dataset tracked with DVC"
else
    echo "⚠ Data file not found at data/UCI_Credit_Card.csv"
fi

# 5. Add DVC files to Git
echo "📝 Adding DVC files to Git..."
git add data/*.dvc data/.gitignore .dvc .dvcignore .gitignore
git add requirements.txt Dockerfile docker-compose.yml
git add README.md DVC_SETUP.md DOCKER.md GITHUB_SETUP.md
git add .github/workflows/
git add -A

# 6. Initial commit
echo "✅ Creating initial commit..."
git commit -m "Initial commit: Credit scoring ML pipeline with DVC, Docker, and GitHub Actions setup"

# 7. Instructions for GitHub
echo ""
echo "📋 Next Steps:"
echo "==============================================="
echo "1. Create repository on GitHub (https://github.com/new)"
echo "2. Add remote:"
echo "   git remote add origin https://github.com/YOUR_USERNAME/credit_scoring_project.git"
echo "3. Push to GitHub:"
echo "   git branch -M main"
echo "   git push -u origin main"
echo "4. Push data to DVC:"
echo "   dvc push"
echo "5. Add GitHub Secrets (Settings → Secrets → New repository secret):"
echo "   - DVC_REMOTE_PATH: ~/dvc-storage (or S3/GCS path)"
echo "   - AWS_ACCESS_KEY_ID (if using S3)"
echo "   - AWS_SECRET_ACCESS_KEY (if using S3)"
echo ""
echo "🎉 Setup complete!"
echo "Run 'git remote add origin https://github.com/YOUR_USERNAME/credit_scoring_project.git' to push"
