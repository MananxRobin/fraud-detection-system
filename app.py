from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import pandas as pd
import uvicorn

# Initialize App
app = FastAPI(title="Fraud Detection System")

# Load Model (Global variable to load only once)
model = joblib.load('fraud_model_lgbm.pkl')

# Define Data Schema
class Transaction(BaseModel):
    step: int
    type: str
    amount: float
    nameOrig: str
    oldbalanceOrg: float
    newbalanceOrig: float
    nameDest: str
    oldbalanceDest: float
    newbalanceDest: float

@app.post("/predict")
def predict_fraud(tx: Transaction):
    # 1. Preprocessing (Must match training logic exactly)
    type_map = {'PAYMENT':0, 'TRANSFER':1, 'CASH_OUT':2, 'DEBIT':3, 'CASH_IN':4}
    
    # Calculate engineered features on the fly
    errorBalanceOrig = tx.newbalanceOrig + tx.amount - tx.oldbalanceOrg
    errorBalanceDest = tx.oldbalanceDest + tx.amount - tx.newbalanceDest
    step_hour = tx.step % 24
    
    # NOTE: in a real system, 'transaction_count_1h' would be queried from Redis here.
    # For this simplified code, we assume a static value or 1.
    transaction_count_1h = 1 

    # Prepare input vector
    features = [[
        step_hour,
        type_map.get(tx.type, 0), # Default to 0 if unknown
        tx.amount,
        tx.oldbalanceOrg,
        tx.newbalanceOrig,
        tx.oldbalanceDest,
        tx.newbalanceDest,
        errorBalanceOrig,
        errorBalanceDest,
        transaction_count_1h
    ]]
    
    # 2. Inference
    # predict_proba returns [prob_legit, prob_fraud]
    prediction_prob = model.predict_proba(features)[0][1]
    is_fraud = prediction_prob > 0.8 # Threshold usually determined by Precision/Recall trade-off

    # 3. Return Result
    return {
        "is_fraud": bool(is_fraud),
        "fraud_probability": float(prediction_prob),
        "alert": "HIGH RISK TRANSACTION" if is_fraud else "Safe"
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)