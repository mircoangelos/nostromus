from sqlalchemy import Column, Integer, String, DateTime, Text, Enum, ForeignKey, Boolean, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from database import Base

class EventType(str, enum.Enum):
    SECURITY_EVENT = "SECURITY_EVENT"
    PERFORMANCE_EVENT = "PERFORMANCE_EVENT"
    OPERATIONAL_EVENT = "OPERATIONAL_EVENT"

class SeverityLevel(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class IncidentStatus(str, enum.Enum):
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"

class AuditAction(str, enum.Enum):
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    VIEW = "VIEW"
    EXECUTE_ACTION = "EXECUTE_ACTION"

# ===== MODELS =====

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(255), unique=True, index=True)  # Keycloak user ID
    username = Column(String(255), unique=True, index=True)
    email = Column(String(255), unique=True, index=True)
    full_name = Column(String(255))
    role = Column(String(50))  # admin, sales, viewer
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    incidents = relationship("Incident", back_populates="created_by_user")
    audit_logs = relationship("AuditLog", back_populates="user")

class Incident(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(Enum(EventType), index=True)
    severity = Column(Enum(SeverityLevel), index=True)
    status = Column(Enum(IncidentStatus), default=IncidentStatus.OPEN, index=True)

    # Event data
    user_id = Column(String(255), index=True)
    ip_address = Column(String(45))  # IPv4 or IPv6
    description = Column(Text)
    event_data = Column(JSON)  # Store full event as JSON

    # AI Agent analysis
    ai_analysis = Column(Text, nullable=True)
    ai_recommendation = Column(Text, nullable=True)

    # Actions taken
    action_taken = Column(String(255), nullable=True)
    action_details = Column(JSON, nullable=True)

    # Tracking
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    created_by_user = relationship("User", back_populates="incidents")
    reports = relationship("Report", back_populates="incident", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="incident")

class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(Integer, ForeignKey("incidents.id"), index=True, nullable=True)
    report_id = Column(String(100), unique=True, index=True)  # REP_YYYYMMDD_HHMMSS

    severity = Column(Enum(SeverityLevel), index=True)
    title = Column(String(255))
    content = Column(Text)  # Full report content

    # AI metadata
    ai_model = Column(String(50))  # e.g., "gemini-2.0-flash"
    ai_response_time = Column(Integer)  # milliseconds

    # User who made the decision
    decision_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Status
    is_published = Column(Boolean, default=False)
    published_at = Column(DateTime, nullable=True)

    # Tracking
    generated_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    incident = relationship("Incident", back_populates="reports", foreign_keys=[incident_id])
    decision_by_user = relationship("User", foreign_keys=[decision_by_id])

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(Integer, ForeignKey("incidents.id"), index=True, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=True)

    action = Column(Enum(AuditAction), index=True)
    resource_type = Column(String(50))  # "incident", "report", "user", etc.
    resource_id = Column(String(255))

    # Details
    old_value = Column(JSON, nullable=True)  # Previous value
    new_value = Column(JSON, nullable=True)  # New value
    description = Column(Text, nullable=True)
    ip_address = Column(String(45))
    user_agent = Column(String(500), nullable=True)

    # Tracking
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    incident = relationship("Incident", back_populates="audit_logs")
    user = relationship("User", back_populates="audit_logs")
