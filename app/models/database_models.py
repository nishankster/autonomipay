"""
SQLAlchemy database models for persistence.

These models track conversion jobs, errors, and audit information.
"""

from datetime import datetime
from enum import Enum

from sqlalchemy import Column, String, Integer, DateTime, Text, Boolean, Float, Enum as SQLEnum
from sqlalchemy.sql import func

from app.config.database import Base


class JobStatus(str, Enum):
    """Job status enumeration."""
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    RETRYING = "RETRYING"


class ConversionJob(Base):
    """Database model for conversion jobs."""
    
    __tablename__ = "conversion_jobs"
    
    id = Column(String(36), primary_key=True)
    filename = Column(String(255), nullable=False)
    status = Column(SQLEnum(JobStatus), default=JobStatus.PENDING, nullable=False)
    
    # File information
    file_size = Column(Integer, nullable=False)
    total_entries = Column(Integer, default=0)
    total_batches = Column(Integer, default=0)
    
    # Processing results
    successful_entries = Column(Integer, default=0)
    failed_entries = Column(Integer, default=0)
    total_amount_cents = Column(Integer, default=0)
    
    # Message publishing
    messages_published = Column(Integer, default=0)
    messages_failed = Column(Integer, default=0)
    
    # Retry information
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Error tracking
    error_message = Column(Text, nullable=True)
    error_details = Column(Text, nullable=True)
    
    # Additional metadata
    source_system = Column(String(100), nullable=True)
    correlation_id = Column(String(36), nullable=True)
    user_id = Column(String(100), nullable=True)


class ConversionError(Base):
    """Database model for conversion errors."""
    
    __tablename__ = "conversion_errors"
    
    id = Column(String(36), primary_key=True)
    job_id = Column(String(36), nullable=False, index=True)
    
    # Error information
    error_type = Column(String(100), nullable=False)
    error_message = Column(Text, nullable=False)
    error_details = Column(Text, nullable=True)
    
    # Context
    record_type = Column(String(10), nullable=True)
    line_number = Column(Integer, nullable=True)
    entry_number = Column(Integer, nullable=True)
    
    # Severity
    severity = Column(String(20), nullable=False)  # INFO, WARNING, ERROR, CRITICAL
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now(), nullable=False)


class AuditLog(Base):
    """Database model for audit logging."""
    
    __tablename__ = "audit_logs"
    
    id = Column(String(36), primary_key=True)
    
    # Action information
    action = Column(String(100), nullable=False)
    resource_type = Column(String(100), nullable=False)
    resource_id = Column(String(100), nullable=True)
    
    # Details
    details = Column(Text, nullable=True)
    result = Column(String(20), nullable=False)  # SUCCESS, FAILURE
    
    # User/System information
    user_id = Column(String(100), nullable=True)
    system_user = Column(String(100), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    
    # Request context
    request_id = Column(String(36), nullable=True)
    correlation_id = Column(String(36), nullable=True)


class MessagePublishLog(Base):
    """Database model for message publishing logs."""
    
    __tablename__ = "message_publish_logs"
    
    id = Column(String(36), primary_key=True)
    job_id = Column(String(36), nullable=False, index=True)
    
    # Message information
    message_id = Column(String(36), nullable=False)
    routing_key = Column(String(255), nullable=False)
    
    # Publishing status
    status = Column(String(20), nullable=False)  # PENDING, PUBLISHED, FAILED
    retry_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    published_at = Column(DateTime, nullable=True)
    
    # Error tracking
    error_message = Column(Text, nullable=True)
