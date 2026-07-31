from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from models_db import Report, Incident
from database import get_db
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/")
async def get_reports(
    skip: int = 0,
    limit: int = 20,
    incident_id: int = None,
    published: bool = None,
    db: Session = Depends(get_db)
):
    """
    Get all reports (paginated)
    Query params:
    - skip: offset
    - limit: max results
    - incident_id: filter by incident
    - published: filter by published status
    """
    query = db.query(Report)

    if incident_id:
        query = query.filter(Report.incident_id == incident_id)

    if published is not None:
        query = query.filter(Report.is_published == published)

    total = query.count()
    reports = query.order_by(Report.created_at.desc()).offset(skip).limit(limit).all()

    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "reports": reports
    }

@router.get("/{report_id}")
async def get_report(report_id: int, db: Session = Depends(get_db)):
    """Get a specific report by ID"""
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report

@router.get("/by-report-id/{report_id_str}")
async def get_report_by_report_id(report_id_str: str, db: Session = Depends(get_db)):
    """Get report by report_id (REP_YYYYMMDD_HHMMSS format)"""
    report = db.query(Report).filter(Report.report_id == report_id_str).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report

@router.get("/incidents/{incident_id}/reports")
async def get_incident_reports(
    incident_id: int,
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Get all reports for a specific incident"""
    # Verify incident exists
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    query = db.query(Report).filter(Report.incident_id == incident_id)
    total = query.count()
    reports = query.order_by(Report.created_at.desc()).offset(skip).limit(limit).all()

    return {
        "incident_id": incident_id,
        "total": total,
        "reports": reports
    }

@router.patch("/{report_id}/publish")
async def publish_report(report_id: int, db: Session = Depends(get_db)):
    """Publish a report"""
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    report.is_published = True
    from datetime import datetime
    report.published_at = datetime.utcnow()

    db.commit()
    db.refresh(report)
    return report

@router.get("/stats/summary")
async def get_reports_summary(db: Session = Depends(get_db)):
    """Get summary statistics about reports"""
    total_reports = db.query(Report).count()
    published_reports = db.query(Report).filter(Report.is_published == True).count()
    unpublished_reports = db.query(Report).filter(Report.is_published == False).count()

    # Group by severity
    from sqlalchemy import func
    severity_count = db.query(
        Report.severity,
        func.count(Report.id).label("count")
    ).group_by(Report.severity).all()

    return {
        "total_reports": total_reports,
        "published": published_reports,
        "unpublished": unpublished_reports,
        "by_severity": [
            {"severity": str(item[0]), "count": item[1]}
            for item in severity_count
        ]
    }
