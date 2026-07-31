from fastapi import APIRouter
from models import HealthResponse

router = APIRouter()

@router.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(
        status="ok",
        services={
            "api": "running",
            "database": "connected",
            "rabbitmq": "connected"
        }
    )
