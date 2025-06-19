import os
import pika
import json
import logging
from typing import Dict, Any
from .queue_message import CreateStatsMessage
from .stats_service import generate_workout_stats

logger = logging.getLogger(__name__)
logging.getLogger("pika").setLevel(logging.WARNING)

class StatsQueueConsumer:
    _instance = None
    _is_initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(StatsQueueConsumer, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._is_initialized:
            self.connection = None
            self.channel = None
            self.exchange_name = "workout.performed"
            self.queue_name = "stats_workout_queue" 
            self._is_initialized = True
            self.connect()
            logger.info("StatsQueueConsumer initialized and connected to RabbitMQ")
            
    def ensure_connection(self):
        if not self.connection or self.connection.is_closed:
            self.connect()
            
    def connect(self):
        logger.debug("Attempting to connect to RabbitMQ")
        credentials = pika.PlainCredentials(
            username=os.getenv("RABBITMQ_DEFAULT_USER", "rabbit"),
            password=os.getenv("RABBITMQ_DEFAULT_PASS", "docker")
        )
        parameters = pika.ConnectionParameters(
            host=os.getenv("RABBITMQ_HOST", "rabbitmq"),
            port=5672,
            credentials=credentials,
            heartbeat=600,
            blocked_connection_timeout=300
        )
        self.connection = pika.BlockingConnection(parameters)
        self.channel = self.connection.channel()
        
        self.channel.exchange_declare(exchange="dlx", exchange_type="direct")
        self.channel.queue_declare(queue=f"{self.queue_name}-dead", durable=True)
        self.channel.queue_bind(
            exchange="dlx",
            queue=f"{self.queue_name}-dead",
            routing_key=f"{self.queue_name}-dead"
        )
        
        self.channel.queue_declare(
            queue=self.queue_name,
            durable=True,
            arguments={
                "x-message-ttl": 60000,
                "x-max-length": 100,
                "x-dead-letter-exchange": "dlx",
                "x-dead-letter-routing-key": f"{self.queue_name}-dead"
            }
        )
        
        self.channel.exchange_declare(exchange=self.exchange_name, exchange_type='fanout')
        self.channel.queue_bind(exchange=self.exchange_name, queue=self.queue_name)


        logger.info(f"Successfully connected to RabbitMQ and declared queue '{self.queue_name}'")

    def onCreateWodMessage(self, ch, method, properties, body):
        try:
            logger.info(f"Starting to process message with delivery-tag: {method.delivery_tag}")
            logger.info("Received raw body: %s", body)
            message = CreateStatsMessage.model_validate_json(body)
            logger.debug(f"Successfully parsed message: {message.model_dump_json()}")
            
            user_email = message.email
            
            try:
                workout_stats = generate_workout_stats(user_email)
                if not workout_stats:
                    raise ValueError("No workout statistics generated")

                logger.info(f"Successfully generated workout statistics for user {user_email}")
                
                ch.basic_ack(delivery_tag=method.delivery_tag)
                logger.debug(f"Successfully acknowledged message {method.delivery_tag}")
                
            except Exception as service_error:
                logger.error(f"Error in generate_workout_stats service for user {user_email}: {str(service_error)}", exc_info=True)
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
                return
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode message: {str(e)}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
        except Exception as e:
            logger.error(f"Unexpected error processing message: {str(e)}", exc_info=True)
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
        
    def start_consuming(self):
        try:
            self.ensure_connection()
            
            self.channel.basic_qos(prefetch_count=1)
            self.channel.basic_consume(
                queue=self.queue_name,
                on_message_callback=self.onCreateWodMessage
            )
            
            logger.info(f"Started consuming from queue '{self.queue_name}'")
            self.channel.start_consuming()
            
        except KeyboardInterrupt:
            logger.info("Received shutdown signal, stopping consumer...")
            self.stop()
        except Exception as e:
            logger.error(f"Error in consumer: {str(e)}", exc_info=True)
            self.stop()
            
    def stop(self):
        try:
            if self.channel and self.channel.is_open:
                self.channel.stop_consuming()
                logger.info("Stopped consuming messages")
            
            if self.connection and not self.connection.is_closed:
                self.connection.close()
                logger.info("Closed RabbitMQ connection")
        except Exception as e:
            logger.error(f"Error while stopping consumer: {str(e)}", exc_info=True)

def run_consumer():
    stats_queue_consumer = StatsQueueConsumer()
    logger.info("Starting consumer")
    stats_queue_consumer.start_consuming()