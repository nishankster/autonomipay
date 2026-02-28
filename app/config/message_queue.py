"""
Message queue configuration and connection management.

This module handles RabbitMQ connection setup, channel creation,
and message publishing/consuming.
"""

import logging
from typing import Optional

import aio_pika
from aio_pika import Connection, Channel, Exchange, Queue

from app.config.settings import settings

logger = logging.getLogger(__name__)

# Global connection and channel
connection: Optional[Connection] = None
channel: Optional[Channel] = None
exchange: Optional[Exchange] = None
queue: Optional[Queue] = None


async def init_mq() -> None:
    """Initialize RabbitMQ connection and setup."""
    global connection, channel, exchange, queue
    
    try:
        # Create connection URL
        url = (
            f"amqp://{settings.RABBITMQ_USERNAME}:"
            f"{settings.RABBITMQ_PASSWORD}@"
            f"{settings.RABBITMQ_HOST}:"
            f"{settings.RABBITMQ_PORT}/"
            f"{settings.RABBITMQ_VHOST}"
        )
        
        # Create connection
        connection = await aio_pika.connect_robust(url)
        logger.info("Connected to RabbitMQ")
        
        # Create channel
        channel = await connection.channel()
        logger.info("RabbitMQ channel created")
        
        # Set prefetch count
        await channel.set_qos(prefetch_count=settings.RABBITMQ_PREFETCH_COUNT)
        
        # Declare exchange
        exchange = await channel.declare_exchange(
            settings.RABBITMQ_EXCHANGE,
            aio_pika.ExchangeType.DIRECT,
            durable=True
        )
        logger.info(f"Exchange '{settings.RABBITMQ_EXCHANGE}' declared")
        
        # Declare main queue
        queue = await channel.declare_queue(
            settings.RABBITMQ_QUEUE,
            durable=True
        )
        logger.info(f"Queue '{settings.RABBITMQ_QUEUE}' declared")
        
        # Bind queue to exchange
        await queue.bind(exchange, routing_key=settings.RABBITMQ_ROUTING_KEY)
        logger.info(f"Queue bound to exchange with routing key '{settings.RABBITMQ_ROUTING_KEY}'")
        
        # Declare dead-letter exchange
        dlx = await channel.declare_exchange(
            f"{settings.RABBITMQ_EXCHANGE}.dlx",
            aio_pika.ExchangeType.DIRECT,
            durable=True
        )
        
        # Declare dead-letter queue
        dlq = await channel.declare_queue(
            f"{settings.RABBITMQ_QUEUE}.dlq",
            durable=True,
            arguments={
                "x-dead-letter-exchange": settings.RABBITMQ_EXCHANGE,
                "x-dead-letter-routing-key": settings.RABBITMQ_ROUTING_KEY,
            }
        )
        
        # Bind DLQ to DLX
        await dlq.bind(dlx, routing_key=f"{settings.RABBITMQ_ROUTING_KEY}.dlq")
        logger.info("Dead-letter queue configured")
        
    except Exception as e:
        logger.error(f"Failed to initialize RabbitMQ: {str(e)}")
        raise


async def close_mq() -> None:
    """Close RabbitMQ connection."""
    global connection, channel
    
    if channel:
        await channel.close()
        logger.info("RabbitMQ channel closed")
    
    if connection:
        await connection.close()
        logger.info("RabbitMQ connection closed")


async def publish_message(
    message_body: str,
    routing_key: Optional[str] = None,
    headers: Optional[dict] = None
) -> bool:
    """
    Publish message to RabbitMQ.
    
    Args:
        message_body: Message content
        routing_key: Routing key (uses default if not provided)
        headers: Message headers
    
    Returns:
        bool: True if successful, False otherwise
    """
    global channel, exchange
    
    if not channel or not exchange:
        logger.error("Message queue not initialized")
        return False
    
    try:
        routing_key = routing_key or settings.RABBITMQ_ROUTING_KEY
        
        # Create message
        message = aio_pika.Message(
            body=message_body.encode() if isinstance(message_body, str) else message_body,
            headers=headers or {},
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
        )
        
        # Publish message
        await exchange.publish(message, routing_key=routing_key)
        logger.info(f"Message published to '{routing_key}'")
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to publish message: {str(e)}")
        return False


async def get_connection() -> Optional[Connection]:
    """Get RabbitMQ connection."""
    return connection


async def get_channel() -> Optional[Channel]:
    """Get RabbitMQ channel."""
    return channel


async def get_exchange() -> Optional[Exchange]:
    """Get RabbitMQ exchange."""
    return exchange


async def get_queue() -> Optional[Queue]:
    """Get RabbitMQ queue."""
    return queue
