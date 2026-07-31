import json
from datetime import datetime
from typing import List, Dict
from models_db import Report
import logging

logger = logging.getLogger(__name__)

class DecisionService:
    """Servicio para procesar decisiones de analyst sobre eventos"""

    DECISION_MAP = {
        1: "CRITICAL_ACTION_REQUIRED",
        2: "ALERT_ISSUED",
        3: "INVESTIGATION_REQUIRED",
        4: "NO_ACTION"
    }

    ACTION_MAP = {
        1: "Account locked | Security alert sent | Incident escalated",
        2: "Alert notification dispatched to security team",
        3: "Full log analysis initiated | Forensics running",
        4: "Event logged for future reference"
    }

    # Demo events (para mostración del panel)
    @staticmethod
    def get_demo_events():
        return [
            {
                "id": "evt_brute_force",
                "type": "SECURITY_EVENT",
                "severity": "HIGH",
                "user_id": "attacker_001",
                "description": "Brute force attack detected - 6 failed login attempts",
                "data": {
                    "ip": "192.168.1.100",
                    "attempts": 6,
                    "time_window": "5 minutes",
                    "resource": "login_endpoint"
                }
            },
            {
                "id": "evt_slow_query",
                "type": "PERFORMANCE_EVENT",
                "severity": "MEDIUM",
                "user_id": "system",
                "description": "Slow database query - exceeds threshold",
                "data": {
                    "duration_ms": 3500,
                    "threshold_ms": 2000,
                    "query": "SELECT * FROM users WHERE...",
                    "resource": "user_list_query"
                }
            },
            {
                "id": "evt_suspicious_activity",
                "type": "SECURITY_EVENT",
                "severity": "HIGH",
                "user_id": "user_admin",
                "description": "Suspicious administrative activity - unusual data export",
                "data": {
                    "action": "bulk_export",
                    "records": 50000,
                    "destination": "external_device",
                    "timestamp": "2026-07-31T20:30:00Z"
                }
            },
            {
                "id": "evt_cpu_spike",
                "type": "OPERATIONAL_EVENT",
                "severity": "MEDIUM",
                "user_id": "system",
                "description": "CPU usage spike detected on production server",
                "data": {
                    "current_usage": 89,
                    "threshold": 80,
                    "server": "prod-api-01",
                    "duration_seconds": 300
                }
            }
        ]

    def get_pending_events(self) -> List[Dict]:
        """Obtiene eventos pendientes (demo)"""
        return self.get_demo_events()

    def process_decision(self, event_id: str, decision: int, notes: str, db, analyst_user=None) -> Report:
        """Procesa una decisión y genera reporte"""

        # Encontrar evento
        event = next((e for e in self.get_demo_events() if e["id"] == event_id), None)
        if not event:
            raise ValueError(f"Evento {event_id} no encontrado")

        if decision not in self.DECISION_MAP:
            raise ValueError(f"Decisión {decision} inválida")

        # Generar reporte
        from datetime import datetime
        from models_db import SeverityLevel

        now = datetime.utcnow()

        # Mapear severidad
        severity_map = {
            "LOW": SeverityLevel.LOW,
            "MEDIUM": SeverityLevel.MEDIUM,
            "HIGH": SeverityLevel.HIGH,
            "CRITICAL": SeverityLevel.CRITICAL
        }

        report = Report(
            report_id=f"REP_{now.strftime('%Y%m%d_%H%M%S')}",
            title=f"Analyst Decision - {event['type']}",
            content=self._generate_report_content(event, decision, notes, analyst_user),
            severity=severity_map.get(event.get("severity", "MEDIUM"), SeverityLevel.MEDIUM),
            ai_model="Human Decision Agent",
            ai_response_time=0,
            decision_by_id=analyst_user.id if analyst_user else None,
            is_published=True,
            generated_at=now
        )

        # Guardar en BD
        db.add(report)
        db.commit()
        db.refresh(report)

        analyst_name = analyst_user.username if analyst_user else "Unknown"
        logger.info(f"✓ Decisión procesada por {analyst_name} para evento {event_id}: {self.DECISION_MAP.get(decision)}")

        return report

    def _generate_report_content(self, event: Dict, decision: int, notes: str, analyst_user=None) -> str:
        """Genera contenido del reporte"""
        analyst_name = analyst_user.full_name if analyst_user else "Unknown Analyst"
        analyst_email = analyst_user.email if analyst_user else "N/A"

        return f"""
NOSTROMUS ANALYST DECISION REPORT
{'='*60}

ANALYST INFORMATION:
• Name: {analyst_name}
• Email: {analyst_email}
• Role: threat_analyst

EVENT DETAILS:
• Type: {event.get('type')}
• Severity: {event.get('severity')}
• User: {event.get('user_id')}
• Description: {event.get('description')}

DATA:
{json.dumps(event.get('data', {}), indent=2)}

ANALYST DECISION:
• Action: {self.DECISION_MAP.get(decision)}
• Notes: {notes if notes else 'N/A'}

RECOMMENDED ACTION:
{self.ACTION_MAP.get(decision, 'N/A')}

TIMESTAMP: {datetime.utcnow().isoformat()}
STATUS: Processed by Human Analyst ({analyst_name})

---
This report was generated based on analyst's manual decision
using the Nostromus Human Decision Agent interface.
        """

    def _generate_analysis(self, event: Dict, decision: int) -> str:
        """Genera análisis del evento"""
        event_type = event.get("type", "UNKNOWN")

        if event_type == "SECURITY_EVENT":
            attempts = event.get("data", {}).get("attempts", 0)
            return f"""
SECURITY ANALYSIS:
The system detected {attempts} failed login attempts from IP {event.get('data', {}).get('ip')}.
This pattern is consistent with a brute force attack.

ANALYST DECISION TAKEN:
The analyst reviewed the event and decided: {self.DECISION_MAP.get(decision)}

ACTION PLAN:
{self.ACTION_MAP.get(decision)}
            """

        elif event_type == "PERFORMANCE_EVENT":
            duration = event.get("data", {}).get("duration_ms", 0)
            return f"""
PERFORMANCE ANALYSIS:
Detected slow query execution: {duration}ms (threshold: 2000ms)
Resource affected: {event.get('data', {}).get('resource')}

ANALYST DECISION TAKEN:
The analyst reviewed the event and decided: {self.DECISION_MAP.get(decision)}

ACTION PLAN:
{self.ACTION_MAP.get(decision)}
            """

        return "Event analyzed by Human Analyst"

    def get_summary(self, db) -> Dict:
        """Obtiene resumen de decisiones"""
        total_reports = db.query(Report).count()
        return {
            "total_decisions": total_reports,
            "pending_events": len(self.PENDING_EVENTS),
            "recent_decisions": total_reports
        }
