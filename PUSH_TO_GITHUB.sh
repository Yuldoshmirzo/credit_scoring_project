#!/bin/bash

# PUSH TO GITHUB - Commands

# ============================================
# Step 1: Replace YOUR_USERNAME below
# ============================================

USERNAME="YOUR_USERNAME"  # Replace with your GitHub username

# ============================================
# Step 2: Run these commands one by one
# ============================================

cd "path/to/credit_scoring_project"

# Add remote repository
git remote add origin https://github.com/$USERNAME/credit-scoring-ml.git

# Verify it was added
git remote -v

# Rename branch to main (if needed)
git branch -M main

# Push all commits to GitHub
git push -u origin main

# ============================================
# Verify on GitHub
# ============================================
# Open in browser: https://github.com/$USERNAME/credit-scoring-ml

echo "✅ Pushed to GitHub!"
echo "Visit: https://github.com/$USERNAME/credit-scoring-ml"

# ============================================
# Optional: Set up DVC remote storage
# ============================================

# Create local DVC storage directory
mkdir -p /path/to/dvc-storage

# Add DVC remote
dvc remote add -d myremote /path/to/dvc-storage

# Push DVC-tracked data
dvc push

# Commit DVC configuration
git add .dvc/config
git commit -m "Configure DVC remote storage"
git push

echo "✅ DVC configured and data pushed!"
