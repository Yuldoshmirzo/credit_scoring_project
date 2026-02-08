"""
Stacked Ensemble Training Module
Trains base models with hyperparameter tuning and meta-model
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np
import pandas as pd
import joblib
import optuna
from optuna.samplers import TPESampler
from optuna.pruners import MedianPruner
from sklearn.ensemble import ExtraTreesClassifier, GradientBoostingClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_validate, StratifiedKFold
from sklearn.base import clone
import warnings
warnings.filterwarnings('ignore')

from data_procession.processing import DataProcessor
from data_procession.data_loader import DataLoader


class StackedEnsembleTrainer:
    """Professional Stacked Ensemble Model"""
    def __init__(self, base_models, meta_model, n_splits=5):
        self.base_models = base_models
        self.meta_model = meta_model
        self.n_splits = n_splits

    def train_base_models(self, X, y):
        self.fitted_base_models = []
        skf = StratifiedKFold(n_splits=self.n_splits, shuffle=True, random_state=42)

        for model in self.base_models:
            study = optuna.create_study(direction='maximize',
                                        sampler=TPESampler(seed=42),
                                        pruner=MedianPruner(n_startup_trials=5))
            func = self.objective_function(model, X, y, skf)
            study.optimize(func, n_trials=20, n_jobs=1)
            best_model = model.set_params(**study.best_params)
            best_model.fit(X, y)
            self.fitted_base_models.append(best_model)
            print(f"Trained {model.__class__.__name__} with best params: {study.best_params}")

    def objective_function(self, model, X, y, skf):
        def func(trial):
            param_grid = self.get_param_grid(model, trial)
            model.set_params(**param_grid)
            scores = cross_validate(model, X, y, cv=skf, scoring='roc_auc', n_jobs=-1)
            return np.mean(scores['test_score'])
        
        return func
    
    def get_param_grid(self, model, trial):
        if isinstance(model, ExtraTreesClassifier):
            return {
                'n_estimators': trial.suggest_int('n_estimators', 50, 300),
                'max_depth': trial.suggest_int('max_depth', 5, 30),
                'min_samples_split': trial.suggest_int('min_samples_split', 2, 10),
                'min_samples_leaf': trial.suggest_int('min_samples_leaf', 1, 5),
                'bootstrap': trial.suggest_categorical('bootstrap', [True, False]),
            }
        elif isinstance(model, KNeighborsClassifier):
            return {
                'n_neighbors': trial.suggest_int('n_neighbors', 3, 15),
                'weights': trial.suggest_categorical('weights', ['uniform', 'distance']),
                'p': trial.suggest_categorical('p', [1, 2]),
            }
        elif isinstance(model, GradientBoostingClassifier):
            return {
                'n_estimators': trial.suggest_int('n_estimators', 50, 300),
                'max_depth': trial.suggest_int('max_depth', 3, 15),
                'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.3, log=True),
                'subsample': trial.suggest_float('subsample', 0.5, 1.0),
                'min_samples_split': trial.suggest_int('min_samples_split', 2, 20),
                'min_samples_leaf': trial.suggest_int('min_samples_leaf', 1, 10),
            }
        return {}
    
    def train_meta_model(self, X_meta, y_meta):
        self.meta_model.fit(X_meta, y_meta)
        print(f'Trained Meta Model: {self.meta_model.__class__.__name__}')

    def fit(self, X, y):
        self.train_base_models(X, y)
        skf = StratifiedKFold(n_splits=self.n_splits, shuffle=True, random_state=42)
        X_meta = np.zeros((X.shape[0], len(self.fitted_base_models)))
        y_meta = y.copy()
        
        print("Generating meta-features using cross-validation...")
        for fold, (train_idx, val_idx) in enumerate(skf.split(X, y)):
            X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
            y_train, y_val = y.iloc[train_idx], y.iloc[val_idx]
            
            # Train temporary models on this fold
            for i, base_model in enumerate(self.base_models):
                temp_model = clone(base_model)
                temp_model.fit(X_train, y_train)
                X_meta[val_idx, i] = temp_model.predict_proba(X_val)[:, 1]
            
            print(f"  ✓ Fold {fold + 1}/{self.n_splits} completed")
        
        # Train meta-model on X_meta and y_meta
        self.train_meta_model(X_meta, y_meta)

    def predict(self, X):
        meta_features = np.zeros((X.shape[0], len(self.fitted_base_models)))
        for i, model in enumerate(self.fitted_base_models):
            meta_features[:, i] = model.predict_proba(X)[:, 1]
        return self.meta_model.predict_proba(meta_features)[:, 1]

if __name__ == '__main__':
    # Load and preprocess data
    file_path = str(Path(__file__).parent.parent.parent / "data" / "UCI_Credit_Card.csv")
    data_loader = DataLoader(filepath=file_path)
    df = data_loader.load_data()
    df = data_loader.clean_data()
    
    # Get feature columns (exclude ID and target)
    columns = [col for col in df.columns if df[col].nunique() > 10 and col != 'ID' and col != 'default.payment.next.month']

    processor = DataProcessor(columns, scaler_type='power')
    X_train, X_test, y_train, y_test = processor.split_data(df, target_col='default.payment.next.month')
    X_train_scaled, X_test_scaled = processor.scale_data(X_train, X_test)

    # Define base models and meta model
    # Calculate scale_pos_weight for handling class imbalance
    scale_pos_weight = sum(y_train == 0) / sum(y_train == 1)
    
    base_models = [
        ExtraTreesClassifier(random_state=42, n_jobs=-1),
        KNeighborsClassifier(),
        GradientBoostingClassifier(random_state=42)
    ]
    meta_model = LogisticRegression(random_state=42, max_iter=1000)

    # Train stacked ensemble
    ensemble_trainer = StackedEnsembleTrainer(base_models, meta_model, n_splits=5)
    ensemble_trainer.fit(X_train_scaled, y_train)

    # Evaluate on test set
    y_pred_proba = ensemble_trainer.predict(X_test_scaled)
    y_pred = (y_pred_proba > 0.5).astype(int)