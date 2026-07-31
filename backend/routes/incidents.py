from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from models import IncidentRequest, EventType, SeverityLevel
from models_db import Incident, IncidentStatus
from database import get_db
from services.incident_service import incident_service
import logging
import json

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_incident(incident: IncidentRequest, db: Session = Depends(get_db)):
    """
    Create a new security/performance incident.
    - Saves to PostgreSQL
    - Publishes event to RabbitMQ for processing by AI Agent
    """
    try:
        # Save to database
        db_incident = Incident(
            event_type=incident.event_type,
            severity=incident.severity,
            status=IncidentStatus.OPEN,
            user_id=incident.data.user_id,
            ip_address=incident.data.ip if incident.data.ip else None,
            description=incident.description,
            event_data=incident.data.dict()
        )
        db.add(db_incident)
        db.commit()
        db.refresh(db_incident)

        logger.info(f"Incident #{db_incident.id} saved to database")

        # Publish to RabbitMQ
        result = await incident_service.create_incident(incident)

        return {
            "status": "success",
            "message": "Incident created, saved to database, and queued for analysis",
            "incident_id": db_incident.id,
            "data": result
        }
    except Exception as e:
        logger.error(f"Error creating incident: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/{incident_id}")
async def get_incident(incident_id: int, db: Session = Depends(get_db)):
    """Get incident by ID"""
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident

@router.get("/")
async def list_incidents(
    skip: int = 0,
    limit: int = 20,
    status_filter: str = None,
    severity_filter: str = None,
    db: Session = Depends(get_db)
):
    """
    Get all incidents (paginated)
    Query params:
    - skip: offset
    - limit: max results
    - status_filter: OPEN, IN_PROGRESS, RESOLVED, CLOSED
    - severity_filter: LOW, MEDIUM, HIGH, CRITICAL
    """
    query = db.query(Incident)

    if status_filter:
        query = query.filter(Incident.status == status_filter)

    if severity_filter:
        query = query.filter(Incident.severity == severity_filter)

    total = query.count()
    incidents = query.order_by(Incident.created_at.desc()).offset(skip).limit(limit).all()

    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "incidents": incidents
    }

@router.patch("/{incident_id}")
async def update_incident(
    incident_id: int,
    status: str = None,
    ai_analysis: str = None,
    ai_recommendation: str = None,
    db: Session = Depends(get_db)
):
    """
    Update incident (used by Report Worker)
    """
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    if status:
        incident.status = status
    if ai_analysis:
        incident.ai_analysis = ai_analysis
    if ai_recommendation:
        incident.ai_recommendation = ai_recommendation

    db.commit()
    db.refresh(incident)
    return incident

# Test endpoints
@router.get("/test/brute-force", tags=["test"])
async def test_brute_force(db: Session = Depends(get_db)):
    """Test endpoint: Simulate a brute force attack"""
    incident = IncidentRequest(
        event_type=EventType.SECURITY_EVENT,
        severity=SeverityLevel.HIGH,
        data={
            "user_id": "test_user",
            "ip": "192.168.1.100",
            "attempts": 6
        },
        description="Brute force attack simulation"
    )
    return await create_incident(incident, db)

@router.get("/test/slow-query", tags=["test"])
async def test_slow_query(db: Session = Depends(get_db)):
    """Test endpoint: Simulate a slow query performance event"""
    incident = IncidentRequest(
        event_type=EventType.PERFORMANCE_EVENT,
        severity=SeverityLevel.MEDIUM,
        data={
            "user_id": "system",
            "resource": "GraphQL Query",
            "action": "SELECT * FROM large_table"
        },
        description="Slow query detected: execution time > 2000ms"
    )
    return await create_incident(incident, db)
