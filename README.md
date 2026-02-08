# Credit Scoring ML Pipeline

A production-ready machine learning pipeline for credit default prediction using stacked ensemble models. Includes data versioning, Docker containerization, MLflow tracking, and FastAPI inference server.

## Features

- **Stacked Ensemble Model**: Combines ExtraTreesClassifier, KNeighborsClassifier, GradientBoostingClassifier with LogisticRegression meta-model
- **Hyperparameter Tuning**: Optuna-based optimization with TPE sampler
- **Data Versioning**: DVC integration for reproducible ML workflows
- **MLflow Tracking**: Experiment tracking, model registry, and artifact management
- **FastAPI**: Production-ready REST API for predictions
- **Docker**: Complete containerization for development and deployment
- **GitHub Actions**: Automated CI/CD with data and model versioning

## Quick Start

### Local Development

```bash
# 1. Clone and setup
git clone https://github.com/YOUR_USERNAME/credit_scoring_project.git
cd credit_scoring_project

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Pull data with DVC
dvc pull

# 5. Run training (generates ensemble_model.pkl)
jupyter notebook src/models/evaluate.ipynb

# 6. View MLflow experiments
mlflow ui  # Open http://localhost:5000

# 7. Start API server
uvicorn Api.main:app --reload  # Open http://localhost:8000/docs
```

### Docker Deployment

```bash
# Start all services (training, MLflow, API)
docker-compose up -d

# Access services:
# - MLflow UI: http://localhost:5000
# - FastAPI: http://localhost:8000

# Interactive development
docker-compose exec credit-scoring bash

# View logs
docker-compose logs -f
```

## Project Structure

```
credit_scoring_project/
├── src/
│   ├── data_procession/
│   │   ├── data_loader.py        # Data loading and cleaning
│   │   └── processing.py         # Feature scaling and splitting
│   ├── models/
│   │   ├── train.py              # Stacked ensemble trainer
│   │   ├── evaluate.ipynb        # Training, evaluation, MLflow logging
│   │   └── predict.py            # Inference module
│   ├── features/
│   │   └── diagnostics.py        # Data visualization
│   ├── utils/
│   │   ├── mlflow_utils.py       # MLflow utilities
│   │   └── model_utils.py        # Model evaluation utilities
│   └── pipelines/
│       └── run_pipeline.py       # Reserved for future use
├── Api/
│   └── main.py                   # FastAPI application
├── data/
│   └── UCI_Credit_Card.csv.dvc   # DVC-tracked dataset
├── tests/
│   ├── test_data.py
│   ├── test_model.py
│   └── test_pipelines.py
├── artifacts/
│   └── ensemble_model.pkl        # Trained model
├── .github/workflows/
│   └── data-versioning.yml       # CI/CD pipeline
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── DVC_SETUP.md                  # Data versioning guide
├── DOCKER.md                     # Docker guide
└── GITHUB_SETUP.md               # GitHub & CI/CD guide
```

## Workflow

### 1. Data Processing (data_procession/)
- Load UCI Credit Card dataset
- Handle missing values (mode for binary, median for numeric)
- Remove duplicates
- Stratified train/test split
- Scale with PowerTransformer (handles skewed financial data)

### 2. Model Training (models/evaluate.ipynb)
- **Base Models**: 
  - ExtraTreesClassifier (n_estimators: 50-300)
  - KNeighborsClassifier (n_neighbors: 3-15)
  - GradientBoostingClassifier (learning_rate: 0.01-0.3)
- **Meta-Model**: LogisticRegression
- **Tuning**: Optuna with TPESampler + MedianPruner
- **Validation**: 5-fold stratified cross-validation

### 3. Evaluation & Tracking (evaluate.ipynb)
- Calculate metrics: ROC-AUC, Accuracy, Precision, Recall, F1
- Log to MLflow with parameters and tags
- Register model to MLflow registry
- Save evaluation dashboard as PNG

### 4. Inference (Api/main.py & predict.py)
- Load trained ensemble model
- Score new applicants in real-time
- Return probability and binary prediction

## Data Versioning (DVC)

```bash
# Track dataset
dvc add data/UCI_Credit_Card.csv

# Configure remote storage (local, S3, GCS)
dvc remote add -d storage /path/to/storage

# Push data
dvc push

# Pull data
dvc pull
```

**See [DVC_SETUP.md](DVC_SETUP.md) for complete guide.**

## Docker

```bash
# Development with docker-compose
docker-compose up -d

# Production with Kubernetes manifests
kubectl apply -f k8s/
```

**See [DOCKER.md](DOCKER.md) for complete guide.**

## FastAPI

```bash
# Run API server
uvicorn Api.main:app --host 0.0.0.0 --port 8000

# Interactive docs: http://localhost:8000/docs
# Predictions: POST /predict
```

### Example Request

```python
import requests

payload = {
    "LIMIT_BAL": 20000,
    "SEX": 1,
    "EDUCATION": 2,
    "MARRIAGE": 2,
    "AGE": 25,
    # ... other features
}

response = requests.post(
    "http://localhost:8000/predict",
    json=payload
)

print(response.json())
# {"probability": 0.23, "prediction": 0}
```

## MLflow

```bash
# View experiments and model registry
mlflow ui

# Access at: http://localhost:5000
```

**Features:**
- Track hyperparameters per experiment
- Log metrics (ROC-AUC, F1, etc.)
- Store model artifacts
- Model registry with versions
- Compare runs side-by-side

## Testing

```bash
# Run all tests
pytest tests/ -v

# Test specific module
pytest tests/test_model.py -v

# With coverage
pytest tests/ --cov=src --cov-report=html
```

## GitHub & CI/CD

### Setup

```bash
git init
git remote add origin https://github.com/YOUR_USERNAME/credit_scoring_project.git
git push -u origin main
```

### Secrets (Settings → Secrets)

- `DVC_REMOTE_PATH`: Path to DVC storage
- `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` (if using S3)
- `DOCKER_USERNAME`, `DOCKER_PASSWORD` (for image push)

### Workflows

-  Data validation on push
-  Model testing on pull requests
-  Automatic artifact upload

**See [GITHUB_SETUP.md](GITHUB_SETUP.md) for complete guide.**

## Configuration

Key parameters in `src/data_procession/processing.py`:

```python
scaler_type = 'power'      # PowerTransformer for skewed data
test_size = 0.2            # 80/20 train/test split
random_state = 42          # Reproducibility
n_splits = 5               # Cross-validation folds
```

In `src/models/train.py`:

```python
n_trials = 20              # Optuna optimization trials
threshold = 0.3            # Decision boundary for predictions
```

## Model Performance

Typical test metrics on UCI Credit Card dataset:

| Metric | Score |
|--------|-------|
| ROC-AUC | 0.78 |
| Accuracy | 0.82 |
| Precision | 0.45 |
| Recall | 0.65 |
| F1-Score | 0.53 |

*Note: Actual performance varies based on data preprocessing and tuning parameters.*

## Environment Variables

```bash
# For production deployment
PYTHONUNBUFFERED=1
MODEL_PATH=/app/artifacts/ensemble_model.pkl
DATA_PATH=/app/data/UCI_Credit_Card.csv
MLFLOW_TRACKING_URI=http://mlflow-server:5000
LOG_LEVEL=INFO
```

## Troubleshooting

### Data Issues
```bash
# Check data integrity
dvc status
dvc dag

# Rebuild data cache
dvc fetch --force
dvc checkout
```

### Model Issues
```bash
# Verify model exists
ls -lh artifacts/ensemble_model.pkl

# Test model loading
python -c "import joblib; joblib.load('artifacts/ensemble_model.pkl')"
```

### Docker Issues
```bash
# Clear Docker cache
docker system prune -a

# Rebuild images
docker-compose build --no-cache

# Check container logs
docker-compose logs credit-scoring
```

## Documentation

- [DVC_SETUP.md](DVC_SETUP.md) - Data versioning guide
- [DOCKER.md](DOCKER.md) - Containerization guide
- [GITHUB_SETUP.md](GITHUB_SETUP.md) - GitHub & CI/CD guide
- [.github/copilot-instructions.md](.github/copilot-instructions.md) - AI Copilot context

## License

MIT License

## Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open Pull Request

## Support

For issues and questions:
1. Check existing GitHub Issues
2. Review troubleshooting in [DOCKER.md](DOCKER.md) or [DVC_SETUP.md](DVC_SETUP.md)
3. Create new Issue with reproduction steps

## Learning Resources

- [DVC Documentation](https://dvc.org/doc)
- [MLflow Documentation](https://mlflow.org/docs/latest/index.html)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Scikit-learn Ensemble Methods](https://scikit-learn.org/stable/modules/ensemble.html)
- [Optuna Documentation](https://optuna.readthedocs.io/)
