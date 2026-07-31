from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum

# Enums
class EventType(str, Enum):
    SECURITY_EVENT = "SECURITY_EVENT"
    PERFORMANCE_EVENT = "PERFORMANCE_EVENT"
    OPERATIONAL_EVENT = "OPERATIONAL_EVENT"

class SeverityLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class IncidentStatus(str, Enum):
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"

# Request/Response Models
class EventData(BaseModel):
    user_id: str
    ip: Optional[str] = None
    attempts: Optional[int] = None
    action: Optional[str] = None
    resource: Optional[str] = None
    additional_context: Optional[Dict[str, Any]] = None

class IncidentRequest(BaseModel):
    event_type: EventType
    severity: SeverityLevel
    data: EventData
    description: str

class IncidentResponse(BaseModel):
    id: int
    event_type: EventType
    severity: SeverityLevel
    status: IncidentStatus
    user_id: str
    created_at: datetime
    updated_at: datetime

class ReportResponse(BaseModel):
    id: int
    incident_id: int
    report_id: str
    severity: SeverityLevel
    content: str
    generated_at: datetime
    created_at: datetime

class HealthResponse(BaseModel):
    status: str
    services: Dict[str, str]
