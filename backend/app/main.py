from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware  # ← CORS FIX ADDED
from pydantic import BaseModel
from typing import Optional
import joblib
import pandas as pd
import numpy as np
import os


app = FastAPI(title="🫀 Cardionova CVD Risk API", version="1.0.0")


# ← CORS MIDDLEWARE FIX (ALLOWS FRONTEND → BACKEND)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # React Vite ports
    allow_credentials=True,
    allow_methods=["*"],  # GET, POST, OPTIONS
    allow_headers=["*"],  # Content-Type, Accept
)


# Load YOUR trained models
MODEL_PATH = "E:/Cardionova/backend/models/cardionova_model.pkl"
SCALER_PATH = "E:/Cardionova/backend/models/scaler.pkl"


try:
    model = joblib.load(MODEL_PATH)
    scaler = joblib.load(SCALER_PATH)
    print("✅ Models loaded successfully!")
except:
    model = None
    scaler = None
    print("⚠️  Using dummy model (run notebook first)")


# Patient input schema (YOUR 15 features)
class PatientData(BaseModel):
    male: int
    age: int
    education: int
    currentSmoker: int
    cigsPerDay: float
    BPMeds: int
    prevalentStroke: int
    prevalentHyp: int
    diabetes: int
    totChol: float
    sysBP: float
    diaBP: float
    BMI: float
    heartRate: float
    glucose: float


@app.get("/")
async def root():
    return {"message": "🫀 Cardionova API LIVE!", "docs": "/docs"}


@app.post("/api/predict")
async def predict_risk(patient: PatientData):
    if model is None:
        return {"error": "Model not loaded. Run notebook export first."}
   
    # Convert to DataFrame + predict
    df = pd.DataFrame([patient.dict()])
    df_scaled = scaler.transform(df)
    risk_prob = model.predict_proba(df_scaled)[0][1]
   
    # Clinical risk category
    risk_category = "HIGH" if risk_prob > 0.15 else "LOW"
   
    return {
        "risk_probability": float(risk_prob),
        "risk_percentage": f"{risk_prob:.1%}",
        "risk_category": risk_category,
        "recommendations": [
            "Consult cardiologist immediately",
            "Start BP medication",
            "Smoking cessation program"
        ] if risk_category == "HIGH" else [
            "Maintain healthy lifestyle",
            "Annual checkup recommended"
        ]
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "auc_score": 0.726  # Your trained model performance
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
