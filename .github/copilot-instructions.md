# AI Copilot Instructions for Credit Scoring Project

## Project Overview
This is a **credit scoring ML pipeline** using the UCI Credit Card dataset. The architecture implements a **stacked ensemble approach** for default prediction, with data processing, hyperparameter tuning (Optuna), and model evaluation components.

## Architecture & Data Flow

```
data/UCI_Credit_Card.csv
    ↓
DataLoader (load + clean duplicates/missing values)
    ↓
DataProcessor (handle outliers, scale with PowerTransformer/QuantileTransformer)
    ↓
Train/Test Split (stratified with target='default.payment.next.month')
    ↓
Stacked Ensemble:
  - Base models: ExtraTreesClassifier, KNeighborsClassifier, SVC, LogisticRegression
  - Meta-model: Ensemble aggregator
  - Tuning: Optuna (TPESampler + MedianPruner)
    ↓
Evaluation & Artifact Storage (ROC-AUC, Precision, Recall, F1)
```

## Key Components

### Data Processing (`src/data_procession/`)
- **`DataLoader`**: Loads CSV, handles missing values (mode for binary, median for numeric), removes duplicates
- **`DataProcessor`**: 
  - Supports 4 scaling strategies: `power`, `quantile`, `standard`, `outlier_removal`
  - IQR-based outlier clipping with configurable multiplier (default=3)
  - Stratified train/test split on target `'default.payment.next.month'`
  - Only scales columns with >10 unique values (excludes ID, target)

### Model Training (`src/models/train.py`)
- **`StackedEnsembleTrainer`**: Multi-level ensemble with cross-validation
- Base model selection varies by hyperparameter tuning run
- Metrics tracked: roc_auc_score, accuracy_score, precision_score, recall_score, f1_score
- Optuna configuration: TPESampler (exploration), MedianPruner (pruning)

### Features & Diagnostics (`src/features/`)
- **`diagnostics.py`**: Generates correlation heatmaps, Gaussian distribution plots, box plots for outlier detection
- Output: PNG artifacts saved to `artifacts/` directory

## Development Patterns

### Path Resolution
Always use `pathlib.Path` with `__file__` for relative imports:
```python
sys.path.insert(0, str(Path(__file__).parent.parent))
file = str(Path(__file__).parent.parent.parent / "data" / "UCI_Credit_Card.csv")
```

### Scaling Strategy Selection
When implementing new preprocessing, default to **PowerTransformer** for skewed financial data. The `scaler_type` parameter controls transformation:
- `'power'`: PowerTransformer (handles skew well for credit data)
- `'quantile'`: QuantileTransformer (uniform/normal output)
- `'outlier_removal'`: IQR clipping + StandardScaler
- `'standard'`: StandardScaler (baseline)

### Column Filtering
Consistently exclude non-numeric/ID columns. Target column `'default.payment.next.month'` must be removed from feature set before scaling.

## Testing & Validation
- Test files in `tests/` parallel to `src/` structure (test_data.py, test_model.py, test_pipelines.py)
- Use stratified k-fold validation (n_splits=5 default)
- Artifacts stored in `artifacts/{before_processing,after_processing}/`

## External Dependencies
- **ML/Tuning**: scikit-learn, optuna, mlflow
- **Web API**: fastapi, uvicorn, pydantic
- **Data**: pandas, numpy
- **Visualization**: matplotlib, seaborn
- **Data Source**: kagglehub (for Kaggle dataset access)

## Critical Workflows

### Running Data Processing
```python
from src.data_procession.processing import DataProcessor
processor = DataProcessor(columns, scaler_type='power')
X_train, X_test, y_train, y_test = processor.split_data(df, target_col='default.payment.next.month')
X_train_scaled, X_test_scaled = processor.scale_data(X_train, X_test)
```

### Hyperparameter Tuning with Optuna
Optuna is configured in `src/models/train.py` with TPESampler for exploration and MedianPruner for pruning:
```python
sampler = TPESampler(seed=42)
pruner = MedianPruner()
study = optuna.create_study(direction='maximize', sampler=sampler, pruner=pruner)
study.optimize(objective, n_trials=100)
```
Define `objective()` function to return validation metric (e.g., roc_auc_score from cross-validation).

### Model Tracking with MLflow
Log experiments to track hyperparameters, metrics, and artifacts:
```python
import mlflow

mlflow.set_experiment("credit_scoring_ensemble")
with mlflow.start_run():
    mlflow.log_params({"scaler_type": "power", "n_splits": 5})
    mlflow.log_metrics({"roc_auc": 0.85, "f1_score": 0.72})
    mlflow.sklearn.log_model(model, "stacked_ensemble")
```
MLflow UI accessible via `mlflow ui` command.

### FastAPI Web Interface (End of Project)
Planned FastAPI server structure in `Api/`:
```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class CreditScoreInput(BaseModel):
    # Features matching UCI_Credit_Card.csv columns
    pass

@app.post("/predict")
def predict(data: CreditScoreInput):
    # Load trained model from MLflow
    # Return prediction + probability
    pass
```

### Generating Diagnostics
Execute `src/features/diagnostics.py` directly to generate correlation/distribution plots before training.

## Notes for AI Agents
- Many pipeline files (data_pipeline.py, model_pipeline.py, run_pipeline.py, evaluate.py, predict.py) are stubs—implementations in progress
- **Optuna tuning**: Focus on completing the `objective()` function in train.py; return cross-validated metric (e.g., mean roc_auc from StratifiedKFold)
- **MLflow integration**: Add logging utilities in `src/utils/mlflow_utils.py` to track params, metrics, and model artifacts; ensure consistent experiment naming
- **FastAPI server**: Will be developed at end of project in `Api/` folder; requires model serialization and input validation
- Ensure all model training validates on stratified folds (imbalanced target)
- Binary classification problem (default vs. no-default)
