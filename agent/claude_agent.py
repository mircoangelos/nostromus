"""
Nostromus AI Agent - Powered by Claude (Anthropic)
Analyzes security/performance events and generates detailed reports
"""

import pika
import json
import logging
import os
from datetime import datetime
from dotenv import load_dotenv
from anthropic import Anthropic

import generatorFirstVersion

load_dotenv()

base_dir = os.path.dirname(os.path.abspath(__file__))
log_path = os.path.join(base_dir, "nostromus_claude.log")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.FileHandler(log_path, mode='a', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("NostromusClaudeAgent")

# Claude setup
api_key = os.getenv("ANTHROPIC_API_KEY")
if not api_key:
    raise ValueError("ANTHROPIC_API_KEY not set in .env")

client = Anthropic()

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
        return "You are a Security Analyst. Analyze security events and provide detailed analysis and recommendations."

def format_event_for_analysis(event_data):
    """Format event data for Claude analysis"""
    return f"""
Event Analysis Request
======================

Event Type: {event_data.get('event_type')}
Severity: {event_data.get('severity')}
User ID: {event_data.get('user_id')}
Timestamp: {datetime.utcnow().isoformat()}

Event Data:
{json.dumps(event_data.get('data', {}), indent=2)}

Description: {event_data.get('description')}

Please analyze this event and provide:
1. Threat Assessment
2. Root Cause Analysis
3. Immediate Actions Recommended
4. Long-term Prevention Measures
5. Impact Assessment
"""

def analyze_event_with_claude(event_data):
    """Analyze event using Claude and generate report"""
    try:
        user_id = event_data.get('user_id', 'Unknown')
        event_type = event_data.get('event_type', 'UNKNOWN')
        severity = event_data.get('severity', 'MEDIUM')

        logger.info(f"Processing {event_type} for user: {user_id} with Claude AI")

        # Load skills/system instructions
        skills = load_skills()

        # Prepare the event for analysis
        event_description = format_event_for_analysis(event_data)

        # Call Claude API
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1500,
            system=skills,
            messages=[
                {
                    "role": "user",
                    "content": event_description
                }
            ]
        )

        analysis_text = response.content[0].text

        logger.info(f"[CLAUDE AGENT]: Analysis complete")
        print(f"\n{'='*60}")
        print(f"[CLAUDE AGENT] - {event_type}")
        print(f"{'='*60}")
        print(analysis_text)
        print(f"{'='*60}\n")

        # Generate report
        report_id = f"REP_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"

        # Extract key recommendations from analysis
        recommendation_prompt = f"""Based on this analysis:

{analysis_text}

Provide a 1-2 sentence executive summary of the immediate action to take."""

        rec_response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=200,
            messages=[
                {
                    "role": "user",
                    "content": recommendation_prompt
                }
            ]
        )

        recommendation = rec_response.content[0].text

        report_data = {
            "report_id": report_id,
            "severity": severity,
            "title": f"AI Security Analysis - {event_type}",
            "content": analysis_text,
            "analysis": analysis_text,
            "recommendation": recommendation,
            "event_type": event_type,
            "user_id": user_id
        }

        logger.info(f"✓ Report generated: {report_id}")
        return report_data

    except Exception as e:
        logger.error(f"Critical failure processing event: {e}")
        return None

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
            "title": report_data.get('title'),
            "content": report_data.get('content', ''),
            "analysis": report_data.get('analysis', ''),
            "recommendation": report_data.get('recommendation', ''),
            "ai_model": "Claude 3.5 Sonnet",
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

def on_event_message(ch, method, properties, body):
    """Callback when event message is received"""
    try:
        event_data = json.loads(body)
        logger.info(f"Received event: {event_data.get('event_type')} for user {event_data.get('user_id')}")

        # Analyze with Claude
        report_data = analyze_event_with_claude(event_data)

        if report_data:
            # Publish report (we'll extract incident_id from event_data if available)
            incident_id = event_data.get('incident_id', 1)  # Default to 1 if not provided
            publish_report(incident_id, report_data)
            ch.basic_ack(delivery_tag=method.delivery_tag)
            logger.info("Event processed successfully")
        else:
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
            logger.warning("Event processing failed, requeuing...")

    except Exception as e:
        logger.error(f"Error processing message: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

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
        report_channel.queue_declare(queue='reports_queue', durable=True)

        logger.info("====================================================")
        logger.info("    NOSTROMUS AI AGENT - CLAUDE POWERED              ")
        logger.info("====================================================")
        logger.info("Listening for events on all queues...")

        # Start consuming
        channel.basic_qos(prefetch_count=1)

        # Consume from all event types
        channel.basic_consume(queue='security_events', on_message_callback=on_event_message)
        channel.basic_consume(queue='performance_events', on_message_callback=on_event_message)
        channel.basic_consume(queue='operational_events', on_message_callback=on_event_message)

        logger.info("Waiting for events...")
        channel.start_consuming()

    except Exception as e:
        logger.error(f"Consumer error: {e}")
    finally:
        if connection:
            connection.close()
            logger.info("RabbitMQ connection closed")

if __name__ == "__main__":
    logger.info("Starting Nostromus Claude Agent...")
    start_consumer()
