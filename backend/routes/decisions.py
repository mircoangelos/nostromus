from fastapi import APIRouter, Depends, HTTPException, Header
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import get_db
from services.decision_service import DecisionService
from services.user_service import UserService
from models_db import Report
import json
import jwt
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/decisions", tags=["decisions"])
decision_service = DecisionService()

class DecisionRequest(BaseModel):
    event_id: str
    decision: int
    notes: str = ""
    analyst_username: str = ""  # Username del analyst que toma la decisión

def extract_user_from_token(authorization: str = Header(None)) -> dict:
    """Extrae información del usuario del token JWT sin validación (para demo)"""
    if not authorization:
        return None

    try:
        # El token viene como "Bearer <token>"
        token = authorization.replace("Bearer ", "")

        # Decodificar sin verificar (solo para demo, en producción verificar con Keycloak public key)
        decoded = jwt.decode(token, options={"verify_signature": False})

        logger.info(f"✓ Token decodificado para usuario: {decoded.get('preferred_username')}")
        return decoded
    except Exception as e:
        logger.warning(f"No se pudo decodificar token: {e}")
        return None

@router.get("/pending-events")
async def get_pending_events():
    """Obtiene eventos pendientes de RabbitMQ"""
    try:
        events = decision_service.get_pending_events()
        return {"success": True, "events": events}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/decide")
async def decide_event(
    request: DecisionRequest,
    db: Session = Depends(get_db),
    authorization: str = Header(None)
):
    """Procesa una decisión sobre un evento y genera reporte"""
    try:
        logger.info(f"Processing decision: event_id={request.event_id}, decision={request.decision}")

        # Obtener usuario del token
        token_data = extract_user_from_token(authorization)
        user = None

        if token_data:
            # Sincronizar usuario de Keycloak con BD
            user = UserService.get_or_create_user(db, token_data)
            logger.info(f"✓ Usuario autenticado: {user.username} (ID: {user.id})")
        elif request.analyst_username:
            # Fallback: usar username del request (para demo/testing)
            user = db.query(UserService.__bases__[0].__dict__.get('User')).filter_by(username=request.analyst_username).first()
            if not user:
                logger.warning(f"Usuario no encontrado: {request.analyst_username}")

        report = decision_service.process_decision(
            event_id=request.event_id,
            decision=request.decision,
            notes=request.notes,
            db=db,
            analyst_user=user
        )
        logger.info(f"Report created: {report.id}")
        return {"success": True, "report_id": report.id, "analyst": user.username if user else "Unknown"}
    except Exception as e:
        import traceback
        logger.error(f"Error in decide_event: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/decisions-summary")
async def get_decisions_summary(db: Session = Depends(get_db)):
    """Obtiene resumen de decisiones tomadas"""
    try:
        summary = decision_service.get_summary(db)
        return {"success": True, "summary": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
