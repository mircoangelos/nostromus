import pika
import json
import logging
import os
from datetime import datetime
from dotenv import load_dotenv
from google import genai
from google.genai import types
import generatorFirstVersion

load_dotenv()

base_dir = os.path.dirname(os.path.abspath(__file__))
log_path = os.path.join(base_dir, "nostromus.log")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.FileHandler(log_path, mode='a', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("NostromusRabbitMQConsumer")

# Note: This file is for Gemini. Use claude_agent.py for Claude instead.
api_key = os.getenv("GEMINI_API_KEY")
model_id = os.getenv("MODEL_NAME", "gemini-2.0-flash")
rabbitmq_url = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")
logger.warning("⚠️  Using Gemini. For Claude, use: python claude_agent.py")

client = genai.Client(api_key=api_key)

# Global RabbitMQ channel for publishing reports
report_channel = None

def load_skills():
    """Load the agent's rule set from the Markdown file."""
    skills_path = os.path.join(base_dir, "agentSkills.md")
    try:
        with open(skills_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        logger.error("Skill set file 'agentSkills.md' not found.")
        return "You are a Security Analyst. If login attempts > 5, lock the user and generate a report."

def publish_report(incident_id, report_data):
    """Publish report to reports_queue"""
    global report_channel
    try:
        if not report_channel:
            logger.warning("Report channel not initialized, skipping report publish")
            return False

        report_channel.queue_declare(queue='reports_queue', durable=True)

        report_payload = {
            "incident_id": incident_id,
            "report_id": report_data.get('report_id'),
            "severity": report_data.get('severity', 'MEDIUM'),
            "title": f"AI Analysis Report - {report_data.get('report_id')}",
            "content": report_data.get('content', ''),
            "analysis": report_data.get('analysis', ''),
            "recommendation": report_data.get('recommendation', ''),
            "ai_model": model_id,
            "ai_response_time": 0,
            "generated_at": datetime.utcnow().isoformat()
        }

        message = json.dumps(report_payload)
        report_channel.basic_publish(
            exchange='',
            routing_key='reports_queue',
            body=message,
            properties=pika.BasicProperties(
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
            )
        )
        logger.info(f"✓ Report published to reports_queue: {report_data.get('report_id')}")
        return True
    except Exception as e:
        logger.error(f"Failed to publish report: {e}")
        return False

def process_event(event_data, incident_id=None):
    """Process an event using Gemini AI Agent with AFC"""
    try:
        user_id = event_data.get('user_id', 'Unknown')
        event_type = event_data.get('event_type', 'UNKNOWN')

        logger.info(f"Processing {event_type} for user: {user_id}")

        skills = load_skills()

        # Call Gemini agent with AFC
        response = client.models.generate_content(
            model=model_id,
            contents=f"Analyze this security event and execute required tools: {json.dumps(event_data)}",
            config=types.GenerateContentConfig(
                system_instruction=skills,
                tools=[
                    generatorFirstVersion.update_user_status,
                    generatorFirstVersion.generate_security_report
                ],
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=False)
            )
        )

        # Display Agent conclusion
        if response.text:
            logger.info(f"[GEMINI AGENT]: {response.text}")
            print(f"\n[GEMINI AGENT]: {response.text}")
        else:
            logger.info("[GEMINI AGENT]: Preventive actions successfully executed.")
            print("\n[GEMINI AGENT]: Preventive actions successfully executed.")

        # Generate report for database
        report_id = f"REP_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        report_data = {
            "report_id": report_id,
            "severity": event_data.get('severity', 'MEDIUM'),
            "content": response.text or "Preventive actions successfully executed.",
            "analysis": response.text or "",
            "recommendation": "Review generated incident report for details"
        }

        # Publish report to RabbitMQ for persistence
        if incident_id:
            publish_report(incident_id, report_data)

        return True
    except Exception as e:
        logger.error(f"Critical failure processing event: {e}")
        return False

def on_message(ch, method, properties, body):
    """Callback when message is received from RabbitMQ"""
    try:
        event_data = json.loads(body)
        logger.info(f"Received event: {event_data}")

        success = process_event(event_data)

        if success:
            ch.basic_ack(delivery_tag=method.delivery_tag)
            logger.info("Event processed successfully")
        else:
            ch.basic_nack(delivery_tag=method.delivery_tag)
            logger.warning("Event processing failed, requeuing...")
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag)

def start_consumer():
    """Start consuming events from RabbitMQ"""
    global report_channel
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
        report_channel = connection.channel()  # Separate channel for publishing reports

        # Declare queues
        channel.queue_declare(queue='security_events', durable=True)
        channel.queue_declare(queue='performance_events', durable=True)
        channel.queue_declare(queue='operational_events', durable=True)

        logger.info("====================================================")
        logger.info("    NOSTROMUS AI AGENT - RABBITMQ CONSUMER STARTED  ")
        logger.info("====================================================")

        # Start consuming
        channel.basic_qos(prefetch_count=1)

        # Consume from all event types
        channel.basic_consume(
            queue='security_events',
            on_message_callback=on_message
        )
        channel.basic_consume(
            queue='performance_events',
            on_message_callback=on_message
        )
        channel.basic_consume(
            queue='operational_events',
            on_message_callback=on_message
        )

        logger.info("Waiting for events...")
        channel.start_consuming()

    except Exception as e:
        logger.error(f"Consumer error: {e}")
    finally:
        if connection:
            connection.close()
            logger.info("RabbitMQ connection closed")

if __name__ == "__main__":
    start_consumer()
