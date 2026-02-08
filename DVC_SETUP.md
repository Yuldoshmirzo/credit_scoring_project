# Data Versioning with DVC

This project uses **DVC (Data Version Control)** to version control the dataset and ML artifacts.

## Setup DVC

```bash
# Install DVC (already in requirements.txt)
pip install dvc

# Initialize DVC in the project
dvc init

# Configure remote storage (using local directory for demo, use S3/GCS in production)
dvc remote add -d storage /path/to/remote/storage
```

## Track Data Files

```bash
# Add data to DVC tracking
dvc add data/UCI_Credit_Card.csv

# This creates data/UCI_Credit_Card.csv.dvc file (commit to git)
git add data/UCI_Credit_Card.csv.dvc data/.gitignore
git commit -m "Track dataset with DVC"

# Add model artifacts
dvc add artifacts/ensemble_model.pkl
git add artifacts/ensemble_model.pkl.dvc artifacts/.gitignore
git commit -m "Track trained model with DVC"
```

## Pull Data from DVC

```bash
# Fetch data from remote storage
dvc pull

# This reconstructs UCI_Credit_Card.csv and ensemble_model.pkl locally
```

## Update Data

```bash
# When data changes, update DVC tracking
dvc add data/UCI_Credit_Card.csv
git add data/UCI_Credit_Card.csv.dvc
git commit -m "Update dataset version"

# Push updated data to remote
dvc push
```

## Remote Storage Options

### Local Storage (Development)
```bash
dvc remote add -d local /path/to/local/storage
```

### AWS S3 (Production)
```bash
dvc remote add -d s3remote s3://my-bucket/dvc-storage
dvc remote modify s3remote region us-east-1
```

### Google Cloud Storage
```bash
dvc remote add -d gcs gs://my-bucket/dvc-storage
```

## Benefits

- **Version Control**: Track dataset versions alongside code
- **Collaboration**: Share large files without storing in git
- **Reproducibility**: Ensure exact data versions for experiments
- **CI/CD Integration**: Automatically fetch correct data in pipelines
