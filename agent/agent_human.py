#!/usr/bin/env python3
"""
Nostromus Human Decision Agent
Simula un agent de IA pero permite decisiones manuales del usuario
Demuestra el flujo completo: RabbitMQ → Análisis → Decisión → BD
"""

import json
import pika
import logging
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger("NostromusHumanAgent")

RABBITMQ_URL = "amqp://guest:guest@localhost:5672/"
QUEUES = ["security_events", "performance_events", "operational_events"]

def connect_rabbitmq():
    """Conecta a RabbitMQ"""
    try:
        connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
        channel = connection.channel()

        # Crear colas si no existen
        for queue in QUEUES:
            channel.queue_declare(queue=queue, durable=True)

        channel.queue_declare(queue="reports_queue", durable=True)

        logger.info("✓ Conectado a RabbitMQ")
        return connection, channel
    except Exception as e:
        logger.error(f"✗ Error conectando a RabbitMQ: {e}")
        return None, None

def format_event(event_data):
    """Formatea el evento para mostrar en consola"""
    print("\n" + "="*70)
    print("🔔 NUEVO EVENTO RECIBIDO")
    print("="*70)

    try:
        event = json.loads(event_data)

        print(f"\n📋 TIPO: {event.get('event_type', 'UNKNOWN')}")
        print(f"🎯 SEVERIDAD: {event.get('severity', 'UNKNOWN')}")
        print(f"👤 USUARIO: {event.get('user_id', 'UNKNOWN')}")
        print(f"📝 DESCRIPCIÓN: {event.get('description', 'N/A')}")

        if "data" in event:
            print(f"\n📊 DATOS ADICIONALES:")
            for key, value in event["data"].items():
                print(f"   {key}: {value}")

        return event
    except json.JSONDecodeError:
        print(f"Raw data: {event_data}")
        return {}

def show_analysis_options(event):
    """Muestra opciones de análisis según el tipo de evento"""
    event_type = event.get("event_type", "").upper()
    severity = event.get("severity", "").upper()

    print("\n" + "-"*70)
    print("🤖 ANÁLISIS DEL AGENT (SIMULADO)")
    print("-"*70)

    recommendations = []

    if event_type == "SECURITY_EVENT":
        attempts = event.get("data", {}).get("attempts", 0)

        if attempts > 5:
            print("\n⚠️  ALERTA: Posible ataque de fuerza bruta detectado")
            print(f"   • {attempts} intentos fallidos de la misma IP")
            print(f"   • Usuario objetivo: {event.get('user_id')}")

            recommendations = [
                "1. BLOQUEAR CUENTA - Lock temporal de 30 minutos",
                "2. ALERTAR - Notificar al equipo de seguridad",
                "3. ANALIZAR - Revisar logs de acceso de las últimas 24h",
                "4. PERMITIR - Permitir reintentos (no recomendado)"
            ]

    elif event_type == "PERFORMANCE_EVENT":
        duration = event.get("data", {}).get("duration_ms", 0)

        if duration > 2000:
            print(f"\n⚠️  ALERTA: Query lenta detectada")
            print(f"   • Duración: {duration}ms (> 2000ms)")
            print(f"   • Recurso: {event.get('data', {}).get('resource', 'Unknown')}")

            recommendations = [
                "1. OPTIMIZAR - Agregar índice a la BD",
                "2. CACHEAR - Implementar cache para esta query",
                "3. PAGINAR - Limitar resultados",
                "4. IGNORAR - Es una query válida (no recomendado)"
            ]

    for rec in recommendations:
        print(f"   {rec}")

    return recommendations

def get_user_decision():
    """Pregunta al usuario qué decisión tomar"""
    print("\n" + "="*70)
    print("👨‍💼 DECISIÓN REQUERIDA")
    print("="*70)

    while True:
        choice = input("\n¿Cuál es tu decisión? (1-4): ").strip()
        if choice in ["1", "2", "3", "4"]:
            return int(choice)
        print("❌ Opción inválida. Intenta de nuevo (1-4).")

def generate_report(event, decision):
    """Genera un reporte basado en la decisión del usuario"""
    now = datetime.now()
    report_id = f"REP_{now.strftime('%Y%m%d_%H%M%S')}"

    decision_map = {
        1: "CRITICAL_ACTION_REQUIRED",
        2: "ALERT_ISSUED",
        3: "INVESTIGATION_REQUIRED",
        4: "NO_ACTION"
    }

    action_map = {
        1: "Account locked | Security alert sent | Incident escalated",
        2: "Alert notification dispatched to security team",
        3: "Full log analysis initiated | Forensics running",
        4: "Event logged for future reference"
    }

    severity_color = {
        "LOW": "🟢",
        "MEDIUM": "🟡",
        "HIGH": "🔴",
        "CRITICAL": "🔴🔴"
    }

    report = {
        "report_id": report_id,
        "event_id": event.get("event_type", "UNKNOWN"),
        "severity": event.get("severity", "UNKNOWN"),
        "title": f"AI Analysis - {event.get('event_type', 'UNKNOWN')}",
        "content": f"""
NOSTROMUS AI INCIDENT ANALYSIS REPORT
{'='*50}

EVENT DETAILS:
• Type: {event.get('event_type')}
• Severity: {severity_color.get(event.get('severity', 'UNKNOWN'), '?')} {event.get('severity')}
• User: {event.get('user_id')}
• Description: {event.get('description')}

DECISION TAKEN: {decision_map.get(decision, 'UNKNOWN')}
ACTION: {action_map.get(decision, 'N/A')}

ANALYSIS:
The event has been processed by the Human Decision Agent.
Based on the provided information and user decision, appropriate
actions have been recommended and will be executed.

TIMESTAMP: {now.isoformat()}
AGENT: NostromusHumanAgent v0.1
        """,
        "recommendation": action_map.get(decision, "N/A"),
        "ai_model": "Human Decision Agent (Simulated)",
        "generated_at": now.isoformat(),
        "user_decision": decision_map.get(decision)
    }

    return report

def publish_report(channel, report):
    """Publica el reporte a la cola"""
    try:
        channel.basic_publish(
            exchange="",
            routing_key="reports_queue",
            body=json.dumps(report),
            properties=pika.BasicProperties(delivery_mode=2)
        )
        logger.info(f"✓ Reporte publicado: {report['report_id']}")
        return True
    except Exception as e:
        logger.error(f"✗ Error publicando reporte: {e}")
        return False

def callback(ch, method, properties, body):
    """Callback cuando llega un evento"""
    try:
        # Parsear y mostrar evento
        event = format_event(body)

        # Mostrar análisis del agent
        recommendations = show_analysis_options(event)

        if recommendations:
            # Obtener decisión del usuario
            decision = get_user_decision()

            # Generar reporte
            report = generate_report(event, decision)

            print("\n" + "="*70)
            print(f"📄 REPORTE GENERADO: {report['report_id']}")
            print("="*70)
            print(report['content'])

            # Publicar reporte
            publish_report(ch, report)

        # Confirmar procesamiento
        ch.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as e:
        logger.error(f"Error procesando evento: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag)

def start_consumer():
    """Inicia el consumer que escucha eventos"""
    connection, channel = connect_rabbitmq()

    if not connection or not channel:
        logger.error("No se pudo conectar a RabbitMQ")
        return

    # Configurar prefetch
    channel.basic_qos(prefetch_count=1)

    # Bind a todas las colas
    for queue in QUEUES:
        channel.basic_consume(queue=queue, on_message_callback=callback)

    print("\n" + "="*70)
    print("🤖 NOSTROMUS HUMAN DECISION AGENT")
    print("="*70)
    print("\n✓ Agent iniciado y escuchando eventos...")
    print(f"✓ Queues: {', '.join(QUEUES)}")
    print("\n⏳ Esperando eventos... (Ctrl+C para salir)\n")

    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        print("\n\n👋 Agent detenido")
        connection.close()

if __name__ == "__main__":
    start_consumer()
