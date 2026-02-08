"""
FastAPI server for Credit Scoring predictions
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sys
from pathlib import Path
import logging
from contextlib import asynccontextmanager
import pandas as pd

# Setup path to import from src
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize model globally
predictor = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load model on startup"""
    global predictor
    try:
        from src.models.predict import CreditScorePredictor
        predictor = CreditScorePredictor()
        logger.info("Model loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        logger.info("Model will be loaded on first request")
    yield

# Initialize FastAPI app
app = FastAPI(
    title="Credit Scoring API",
    description="Predict credit default probability",
    version="1.0.0",
    lifespan=lifespan
)


class CustomerData(BaseModel):
    """Single customer credit features"""
    ID: int
    LIMIT_BAL: float
    AGE: int
    BILL_AMT1: float
    BILL_AMT2: float
    BILL_AMT3: float
    BILL_AMT4: float
    BILL_AMT5: float
    BILL_AMT6: float
    PAY_AMT1: float
    PAY_AMT2: float
    PAY_AMT3: float
    PAY_AMT4: float
    PAY_AMT5: float
    PAY_AMT6: float
    PAY_1: int
    PAY_2: int
    PAY_3: int
    PAY_4: int
    PAY_5: int
    PAY_6: int
    EDUCATION: int
    MARRIAGE: int
    SEX: int
    AGE_GROUP: int


class BatchPredictionRequest(BaseModel):
    """Batch prediction request"""
    data: list[dict]


class PredictionResponse(BaseModel):
    """Prediction response"""
    ID: int
    default_probability: float
    default_prediction: int
    default_label: str
    risk_level: str


@app.get("/")
def read_root():
    """Root endpoint"""
    return {
        "message": "Credit Scoring API",
        "endpoints": {
            "predict": "/predict",
            "batch_predict": "/batch_predict",
            "health": "/health"
        }
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    if predictor is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    return {"status": "healthy", "model": "credit_scoring_ensemble"}


@app.post("/predict", response_model=PredictionResponse)
def predict_single(customer: CustomerData):
    """
    Predict default probability for single customer
    
    Example:
    {
        "ID": 1,
        "LIMIT_BAL": 20000,
        "AGE": 24,
        "BILL_AMT1": 3913,
        "BILL_AMT2": 3102,
        ...
    }
    """
    if predictor is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        # Convert to DataFrame
        df = pd.DataFrame([customer.dict()])
        
        # Make prediction
        result = predictor.predict(df)
        
        # Add ID to response
        result['ID'] = customer.ID
        
        return PredictionResponse(**result)
        
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/batch_predict")
def predict_batch(request: BatchPredictionRequest):
    """
    Predict default probability for batch of customers
    
    Example:
    {
        "data": [
            {"ID": 1, "LIMIT_BAL": 20000, "AGE": 24, ...},
            {"ID": 2, "LIMIT_BAL": 120000, "AGE": 26, ...}
        ]
    }
    """
    if predictor is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        # Convert to DataFrame
        df = pd.DataFrame(request.data)
        
        # Make predictions
        results = predictor.predict_batch(df)
        
        # Convert to dict list
        return results.to_dict(orient='records')
        
    except Exception as e:
        logger.error(f"Batch prediction error: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/model_info")
def model_info():
    """Get model information"""
    return {
        "name": "credit_scoring_ensemble",
        "type": "StackedEnsemble",
        "base_models": [
            "ExtraTreesClassifier",
            "KNeighborsClassifier",
            "GradientBoostingClassifier"
        ],
        "meta_model": "LogisticRegression",
        "input_features": 25,
        "classes": ["No Default", "Default"],
        "threshold": 0.5
    }


if __name__ == "__main__":
    import uvicorn
    
    logger.info("Starting Credit Scoring API server...")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
