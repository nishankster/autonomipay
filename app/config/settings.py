"""
Application settings and configuration management.

This module handles all configuration from environment variables
and provides a centralized settings object.
"""

from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    APP_NAME: str = "ACH to RTP Conversion Service"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    PORT: int = 8080
    HOST: str = "0.0.0.0"
    CORS_ORIGINS: List[str] = ["*"]
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/ach_rtp_db"
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10
    DATABASE_POOL_RECYCLE: int = 3600
    DATABASE_ECHO: bool = False
    
    # RabbitMQ
    RABBITMQ_HOST: str = "localhost"
    RABBITMQ_PORT: int = 5672
    RABBITMQ_USERNAME: str = "guest"
    RABBITMQ_PASSWORD: str = "guest"
    RABBITMQ_VHOST: str = "/"
    RABBITMQ_EXCHANGE: str = "rtp-gateway"
    RABBITMQ_ROUTING_KEY: str = "rtp.credit.transfer"
    RABBITMQ_QUEUE: str = "rtp-messages"
    RABBITMQ_PREFETCH_COUNT: int = 10
    
    # ACH Processing
    ACH_MAX_FILE_SIZE: int = 10485760  # 10 MB
    ACH_MAX_ENTRIES_PER_BATCH: int = 10000
    ACH_BATCH_TIMEOUT_SECONDS: int = 30
    
    # RTP Message
    RTP_MESSAGE_TIMEOUT_MS: int = 30000
    RTP_MESSAGE_SCHEMA_VALIDATION: bool = True
    
    # Job Processing
    JOB_RETENTION_DAYS: int = 30
    JOB_MAX_RETRIES: int = 3
    JOB_RETRY_DELAY_SECONDS: int = 60
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"  # json or text
    
    # Monitoring
    METRICS_ENABLED: bool = True
    AUDIT_LOGGING_ENABLED: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
