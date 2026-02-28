"""
Audit logging for compliance and troubleshooting.

This module provides structured audit logging for all
significant operations.
"""

import logging
import json
from datetime import datetime
from typing import Optional, Any
import uuid

from pythonjsonlogger import jsonlogger

logger = logging.getLogger(__name__)


class AuditLogger:
    """Audit logger for tracking significant events."""
    
    @staticmethod
    def log_file_upload(
        filename: str,
        file_size: int,
        job_id: str,
        source_system: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> None:
        """Log file upload event."""
        AuditLogger._log_event(
            action="FILE_UPLOAD",
            resource_type="ACH_FILE",
            resource_id=filename,
            details={
                "job_id": job_id,
                "file_size": file_size,
                "source_system": source_system
            },
            user_id=user_id,
            result="SUCCESS"
        )
    
    @staticmethod
    def log_conversion_start(
        job_id: str,
        filename: str,
        total_entries: int
    ) -> None:
        """Log conversion job start."""
        AuditLogger._log_event(
            action="CONVERSION_START",
            resource_type="CONVERSION_JOB",
            resource_id=job_id,
            details={
                "filename": filename,
                "total_entries": total_entries
            },
            result="SUCCESS"
        )
    
    @staticmethod
    def log_conversion_complete(
        job_id: str,
        successful_entries: int,
        failed_entries: int,
        messages_published: int
    ) -> None:
        """Log conversion job completion."""
        AuditLogger._log_event(
            action="CONVERSION_COMPLETE",
            resource_type="CONVERSION_JOB",
            resource_id=job_id,
            details={
                "successful_entries": successful_entries,
                "failed_entries": failed_entries,
                "messages_published": messages_published
            },
            result="SUCCESS"
        )
    
    @staticmethod
    def log_conversion_failure(
        job_id: str,
        error_message: str,
        error_type: str
    ) -> None:
        """Log conversion job failure."""
        AuditLogger._log_event(
            action="CONVERSION_FAILURE",
            resource_type="CONVERSION_JOB",
            resource_id=job_id,
            details={
                "error_type": error_type,
                "error_message": error_message
            },
            result="FAILURE"
        )
    
    @staticmethod
    def log_message_published(
        job_id: str,
        message_id: str,
        routing_key: str
    ) -> None:
        """Log message published event."""
        AuditLogger._log_event(
            action="MESSAGE_PUBLISHED",
            resource_type="RTP_MESSAGE",
            resource_id=message_id,
            details={
                "job_id": job_id,
                "routing_key": routing_key
            },
            result="SUCCESS"
        )
    
    @staticmethod
    def log_message_publishing_failure(
        job_id: str,
        message_id: str,
        error_message: str
    ) -> None:
        """Log message publishing failure."""
        AuditLogger._log_event(
            action="MESSAGE_PUBLISHING_FAILURE",
            resource_type="RTP_MESSAGE",
            resource_id=message_id,
            details={
                "job_id": job_id,
                "error_message": error_message
            },
            result="FAILURE"
        )
    
    @staticmethod
    def log_job_retry(
        job_id: str,
        retry_count: int
    ) -> None:
        """Log job retry event."""
        AuditLogger._log_event(
            action="JOB_RETRY",
            resource_type="CONVERSION_JOB",
            resource_id=job_id,
            details={
                "retry_count": retry_count
            },
            result="SUCCESS"
        )
    
    @staticmethod
    def log_database_error(
        operation: str,
        error_message: str
    ) -> None:
        """Log database error."""
        AuditLogger._log_event(
            action="DATABASE_ERROR",
            resource_type="DATABASE",
            details={
                "operation": operation,
                "error_message": error_message
            },
            result="FAILURE"
        )
    
    @staticmethod
    def log_queue_error(
        operation: str,
        error_message: str
    ) -> None:
        """Log message queue error."""
        AuditLogger._log_event(
            action="QUEUE_ERROR",
            resource_type="MESSAGE_QUEUE",
            details={
                "operation": operation,
                "error_message": error_message
            },
            result="FAILURE"
        )
    
    @staticmethod
    def _log_event(
        action: str,
        resource_type: str,
        resource_id: Optional[str] = None,
        details: Optional[dict] = None,
        user_id: Optional[str] = None,
        result: str = "SUCCESS"
    ) -> None:
        """
        Log an audit event.
        
        Args:
            action: Action being performed
            resource_type: Type of resource
            resource_id: ID of resource
            details: Additional details
            user_id: User performing action
            result: Result of action (SUCCESS/FAILURE)
        """
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_id": str(uuid.uuid4()),
            "action": action,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "result": result,
            "user_id": user_id or "system",
            "details": details or {}
        }
        
        logger.info(json.dumps(event))


def setup_audit_logging():
    """Setup JSON logging for audit trail."""
    # Configure JSON logger
    json_handler = logging.StreamHandler()
    json_formatter = jsonlogger.JsonFormatter()
    json_handler.setFormatter(json_formatter)
    
    # Add handler to audit logger
    audit_logger = logging.getLogger("audit")
    audit_logger.addHandler(json_handler)
    audit_logger.setLevel(logging.INFO)
    
    logger.info("Audit logging initialized")
