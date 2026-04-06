from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.database import ping_db
from app.routes import predict, report
from app.config import get_settings

settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    ping_db()        # sync call, no await needed
    yield
app = FastAPI(
    title="Cardionova API",
    description="Cardiovascular Risk Prediction — No login required.",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(predict.router)
app.include_router(report.router)

@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok", "message": "Cardionova API is running 🚀"}
