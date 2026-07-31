import logging
from models import IncidentRequest, EventType, SeverityLevel
from services.rabbitmq_service import rabbitmq_service

logger = logging.getLogger(__name__)

class IncidentService:
    """
    Service to handle incident ingestion and event publishing to RabbitMQ
    """

    async def create_incident(self, incident: IncidentRequest) -> dict:
        """
        Create an incident and publish it to RabbitMQ for downstream processing
        """
        try:
            event_data = {
                "event_type": incident.event_type.value,
                "severity": incident.severity.value,
                "user_id": incident.data.user_id,
                "data": incident.data.dict(),
                "description": incident.description,
            }

            # Route to appropriate queue based on event type
            if incident.event_type == EventType.SECURITY_EVENT:
                queue_name = "security_events"
            elif incident.event_type == EventType.PERFORMANCE_EVENT:
                queue_name = "performance_events"
            else:
                queue_name = "operational_events"

            # Publish to RabbitMQ
            success = rabbitmq_service.publish_event(queue_name, event_data)

            if success:
                return {
                    "status": "created",
                    "queue": queue_name,
                    "event": event_data
                }
            else:
                raise Exception("Failed to publish event to RabbitMQ")

        except Exception as e:
            logger.error(f"Error creating incident: {e}")
            raise

incident_service = IncidentService()
