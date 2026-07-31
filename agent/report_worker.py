"""
Report Worker - Consumes reports_queue from RabbitMQ and saves to PostgreSQL
Listens for report events from AI Agent and persists them in database
"""

import pika
import json
import logging
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models_db import Report, Incident, IncidentStatus
from database import Base

load_dotenv()

base_dir = os.path.dirname(os.path.abspath(__file__))
log_path = os.path.join(base_dir, "report_worker.log")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.FileHandler(log_path, mode='a', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("ReportWorker")

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://nostromus:nostromuspass@localhost:5432/nostromus")
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables
Base.metadata.create_all(bind=engine)

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")

def save_report_to_db(report_data):
    """Save report to PostgreSQL database"""
    db = SessionLocal()
    try:
        # Verify incident exists
        incident_id = report_data.get('incident_id')
        incident = db.query(Incident).filter(Incident.id == incident_id).first()

        if not incident:
            logger.warning(f"Incident {incident_id} not found for report {report_data.get('report_id')}")
            return False

        # Create report record
        report = Report(
            incident_id=incident_id,
            report_id=report_data.get('report_id'),
            severity=report_data.get('severity'),
            title=report_data.get('title', 'Incident Report'),
            content=report_data.get('content'),
            ai_model=report_data.get('ai_model', 'gemini-2.0-flash'),
            ai_response_time=report_data.get('ai_response_time', 0),
            is_published=False,
            generated_at=datetime.fromisoformat(report_data.get('generated_at', datetime.utcnow().isoformat()))
        )

        db.add(report)

        # Update incident status
        incident.status = IncidentStatus.IN_PROGRESS
        incident.ai_analysis = report_data.get('analysis')
        incident.ai_recommendation = report_data.get('recommendation')

        db.commit()
        db.refresh(report)

        logger.info(f"✓ Report #{report.id} saved to database for incident #{incident_id}")
        return True

    except Exception as e:
        logger.error(f"✗ Failed to save report: {e}")
        db.rollback()
        return False
    finally:
        db.close()

def on_report_message(ch, method, properties, body):
    """Callback when report message is received"""
    try:
        report_data = json.loads(body)
        logger.info(f"Received report: {report_data.get('report_id')}")

        success = save_report_to_db(report_data)

        if success:
            ch.basic_ack(delivery_tag=method.delivery_tag)
            logger.info("Report processed and saved successfully")
        else:
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
            logger.warning("Report processing failed, requeuing...")

    except Exception as e:
        logger.error(f"Error processing report message: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

def start_worker():
    """Start the Report Worker"""
    try:
        credentials = pika.PlainCredentials('guest', 'guest')
        parameters = pika.ConnectionParameters(
            host='localhost',
            credentials=credentials,
            connection_attempts=5,
            retry_delay=2
        )
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()

        # Declare queue
        channel.queue_declare(queue='reports_queue', durable=True)

        logger.info("====================================================")
        logger.info("    NOSTROMUS REPORT WORKER - STARTED               ")
        logger.info("====================================================")
        logger.info("Listening for reports on: reports_queue")

        # Start consuming
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(
            queue='reports_queue',
            on_message_callback=on_report_message
        )

        logger.info("Waiting for reports...")
        channel.start_consuming()

    except Exception as e:
        logger.error(f"Worker error: {e}")
    finally:
        if connection:
            connection.close()
            logger.info("RabbitMQ connection closed")

if __name__ == "__main__":
    logger.info("Connecting to database and RabbitMQ...")
    start_worker()
