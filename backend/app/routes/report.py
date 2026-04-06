from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import Response
from app.models import SendReportRequest, PredictionInput
from app.ml_pipeline.predictor import predict
from app.services.pdf_service import generate_pdf
from app.services.email_service import send_report_email
from app.database import predictions_collection
from datetime import datetime, timezone

router = APIRouter(prefix="/api", tags=["Report"])

@router.post("/generate-report")
async def generate_report(data: PredictionInput):
    try:
        result = predict(data)
        pdf_bytes = generate_pdf(result, data.model_dump())
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": 'attachment; filename="Cardionova_Heart_Report.pdf"'}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")

@router.post("/send-report")
async def send_report(request: SendReportRequest, background_tasks: BackgroundTasks):
    try:
        result = predict(request.input_data)
        pdf_bytes = generate_pdf(result, request.input_data.model_dump())

        # ← removed 'await' — pymongo is synchronous
        predictions_collection.update_one(
            {"_id": request.prediction_id},
            {"$set": {
                "email": request.email,
                "report_sent_at": datetime.now(timezone.utc).isoformat()
            }}
        )

        background_tasks.add_task(
            send_report_email,
            str(request.email),
            pdf_bytes,
            result["risk_level"],
            result.get("risk_probability") or result.get("probability") or 0.0
        )

        return {
            "success": True,
            "message": f"Report is being sent to {request.email}. Check your inbox shortly.",
            "risk_level": result["risk_level"],
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send report: {str(e)}")
