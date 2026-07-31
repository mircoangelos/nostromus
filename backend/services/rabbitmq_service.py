import pika
import json
import logging
from typing import Callable
from config import settings

logger = logging.getLogger(__name__)

class RabbitMQService:
    def __init__(self):
        self.connection = None
        self.channel = None
        self.consumers = {}

    async def connect(self):
        try:
            credentials = pika.PlainCredentials('guest', 'guest')
            parameters = pika.ConnectionParameters(
                host='rabbitmq',
                credentials=credentials,
                connection_attempts=5,
                retry_delay=2
            )
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            logger.info("✓ Connected to RabbitMQ")
            return True
        except Exception as e:
            logger.error(f"✗ RabbitMQ connection failed: {e}")
            return False

    def declare_queue(self, queue_name: str):
        if not self.channel:
            raise RuntimeError("RabbitMQ not connected")
        self.channel.queue_declare(queue=queue_name, durable=True)
        logger.info(f"Queue declared: {queue_name}")

    def publish_event(self, queue_name: str, event_data: dict) -> bool:
        try:
            if not self.channel:
                raise RuntimeError("RabbitMQ not connected")

            self.declare_queue(queue_name)

            message = json.dumps(event_data)
            self.channel.basic_publish(
                exchange='',
                routing_key=queue_name,
                body=message,
                properties=pika.BasicProperties(
                    delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
                )
            )
            logger.info(f"Event published to {queue_name}: {event_data}")
            return True
        except Exception as e:
            logger.error(f"Failed to publish event: {e}")
            return False

    def start_consuming(self, queue_name: str, callback: Callable):
        try:
            if not self.channel:
                raise RuntimeError("RabbitMQ not connected")

            self.declare_queue(queue_name)

            def on_message(ch, method, properties, body):
                try:
                    event_data = json.loads(body)
                    callback(event_data)
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                except Exception as e:
                    logger.error(f"Error processing message: {e}")
                    ch.basic_nack(delivery_tag=method.delivery_tag)

            self.channel.basic_qos(prefetch_count=1)
            self.channel.basic_consume(queue=queue_name, on_message_callback=on_message)
            logger.info(f"Started consuming from {queue_name}")
            self.channel.start_consuming()
        except Exception as e:
            logger.error(f"Consumer error: {e}")

    def close(self):
        if self.connection:
            self.connection.close()
            logger.info("RabbitMQ connection closed")

# Singleton instance
rabbitmq_service = RabbitMQService()

async def init_rabbitmq():
    await rabbitmq_service.connect()

async def close_rabbitmq():
    rabbitmq_service.close()
