from fastapi import APIRouter, HTTPException
from app.models import PredictionInput, PredictionResponse
from app.ml_pipeline.predictor import predict
from app.database import predictions_collection
from datetime import datetime, timezone
import uuid

router = APIRouter(prefix="/api", tags=["Prediction"])

@router.post("/predict", response_model=PredictionResponse)
async def predict_cvd_risk(data: PredictionInput):
    try:
        result = predict(data)
        prediction_id = str(uuid.uuid4())

        record = {
            "_id": prediction_id,
            "input": data.model_dump(),
            "probability": result["probability"],
            "risk_level": result["risk_level"],
            "shap_values": result["all_shap"],
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        predictions_collection.insert_one(record)   # ← no await, sync pymongo

        return PredictionResponse(
            prediction_id=prediction_id,
            cvd_probability=round(result["probability"], 4),
            cvd_probability_pct=f"{result['probability'] * 100:.1f}%",
            risk_level=result["risk_level"],
            recommendation=result["recommendation"],
            top_risk_factors=result["top_risk_factors"],
            engineered_features=result["engineered_features"],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

