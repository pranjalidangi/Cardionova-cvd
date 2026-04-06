from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional


class PredictionInput(BaseModel):
    name: Optional[str] = None
    male: int = Field(..., ge=0, le=1)
    age: int = Field(..., ge=18, le=100)
    education: int = Field(..., ge=1, le=4)
    currentSmoker: int = Field(..., ge=0, le=1)
    cigsPerDay: float = Field(..., ge=0, le=100)
    BPMeds: int = Field(..., ge=0, le=1)
    prevalentStroke: int = Field(..., ge=0, le=1)
    prevalentHyp: int = Field(..., ge=0, le=1)
    diabetes: int = Field(..., ge=0, le=1)
    totChol: float = Field(..., ge=100, le=600)
    sysBP: float = Field(..., ge=70, le=300)
    diaBP: float = Field(..., ge=40, le=200)
    BMI: float = Field(..., ge=10, le=70)
    heartRate: float = Field(..., ge=30, le=200)
    glucose: float = Field(..., ge=40, le=500)


class ShapFactor(BaseModel):
    feature: str
    value: float
    shap_value: float
    direction: str
    magnitude: str


class PredictionResponse(BaseModel):
    prediction_id: str
    cvd_probability: float
    cvd_probability_pct: str
    risk_level: str
    recommendation: str
    top_risk_factors: List[ShapFactor]
    engineered_features: dict


class SendReportRequest(BaseModel):
    email: EmailStr
    prediction_id: str
    input_data: PredictionInput
