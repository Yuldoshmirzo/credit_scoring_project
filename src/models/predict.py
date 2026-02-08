"""
Production Prediction Module
Loads trained StackedEnsembleTrainer from artifact and makes predictions
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
import joblib
import logging
from typing import Dict, List, Union

from data_procession.data_loader import DataLoader
from data_procession.processing import DataProcessor

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CreditScorePredictor:
    """Load trained ensemble model and make predictions"""
    
    def __init__(self):
        """Initialize predictor by loading ensemble trainer"""
        self.model = None
        self.columns = None
        self._load_model()
    
    def _load_model(self):
        """Load ensemble trainer from artifact"""
        try:
            model_path = Path(__file__).parent.parent.parent / "artifacts" / "ensemble_model.pkl"
            if not model_path.exists():
                raise FileNotFoundError(f"Model not found at {model_path}")
            
            self.model = joblib.load(model_path)
            logger.info(f"Model loaded successfully from {model_path}")
            
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise
    
    def predict(self, X: pd.DataFrame) -> Union[Dict, List[Dict]]:
        """
        Make predictions on new data
        
        Args:
            X: DataFrame with raw features (all columns from split_data)
            
        Returns:
            Single dict for 1 row, list of dicts for multiple rows
        """
        try:
            # The model expects the same features it was trained with
            # Don't filter - pass all columns as-is
            
            # StackedEnsembleTrainer.predict handles scaling internally
            y_proba = self.model.predict(X)
            
            # Handle output format
            if len(y_proba.shape) == 2:
                y_proba = y_proba[:, 1] if y_proba.shape[1] > 1 else y_proba[:, 0]
            
            # Format results
            results = []
            for idx in range(len(X)):
                prob = float(y_proba[idx])
                pred = int(prob > 0.5)
                risk = self._get_risk_level(prob)
                
                results.append({
                    'default_probability': round(prob, 4),
                    'default_prediction': pred,
                    'default_label': 'Default' if pred == 1 else 'No Default',
                    'risk_level': risk
                })
            
            # Return single dict for 1 row, list for multiple
            return results[0] if len(results) == 1 else results
            
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            raise
    
    def predict_batch(self, X: pd.DataFrame) -> pd.DataFrame:
        """Make predictions on batch and return as DataFrame"""
        predictions = self.predict(X)
        
        # Convert to list if single prediction
        if not isinstance(predictions, list):
            predictions = [predictions]
        
        return pd.DataFrame(predictions)
    
    @staticmethod
    def _get_risk_level(probability: float) -> str:
        """Classify risk based on default probability"""
        if probability < 0.2:
            return "Low"
        elif probability < 0.4:
            return "Medium"
        elif probability < 0.6:
            return "High"
        else:
            return "Very High"


if __name__ == "__main__":
    logger.info("Credit Scoring Prediction Module")
    logger.info("=" * 60)
    
    try:
        # Load sample data
        file_path = str(Path(__file__).parent.parent.parent / "data" / "UCI_Credit_Card.csv")
        data_loader = DataLoader(file_path)
        df = data_loader.load_data()
        df = data_loader.clean_data()
        
        # Get test set
        columns = [col for col in df.columns if df[col].nunique() > 10 and col != 'ID' 
                   and col != 'default.payment.next.month']
        processor = DataProcessor(columns, scaler_type='power')
        X_train, X_test, _, _ = processor.split_data(df, target_col='default.payment.next.month')
        
        # Make predictions
        logger.info("\nMaking predictions on first 10 test samples...")
        logger.info("=" * 60)
        
        predictor = CreditScorePredictor()
        results = predictor.predict_batch(X_test.iloc[:10])
        
        print("\nPredictions:")
        print(results.to_string())
        print("\n" + "=" * 60)
        print("Prediction module working correctly!")
        
    except Exception as e:
        logger.error(f"Error: {e}")
        logger.info("Ensure: 1) Train ensemble model, 2) Save artifact")
