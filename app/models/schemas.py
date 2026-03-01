"""
Pydantic schemas for API request/response validation.
"""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field


class FileUploadRequest(BaseModel):
    """Request model for file upload."""
    
    filename: str = Field(..., description="Name of the ACH file")
    source_system: Optional[str] = Field(None, description="Source system identifier")
    correlation_id: Optional[str] = Field(None, description="Correlation ID for tracking")


class FileUploadResponse(BaseModel):
    """Response model for file upload."""
    
    job_id: str = Field(..., description="Unique job identifier")
    filename: str = Field(..., description="Uploaded filename")
    status: str = Field(..., description="Job status")
    #created_at: datetime = Field(..., description="Job creation timestamp")
    created_at: datetime = Field(default_factory=datetime.now, description="Job creation timestamp")



class JobStatusResponse(BaseModel):
    """Response model for job status."""
    
    job_id: str = Field(..., description="Job identifier")
    filename: str = Field(..., description="Filename")
    status: str = Field(..., description="Current status")
    
    # Processing statistics
    total_entries: int = Field(..., description="Total entries in file")
    successful_entries: int = Field(..., description="Successfully processed entries")
    failed_entries: int = Field(..., description="Failed entries")
    
    # Message publishing
    messages_published: int = Field(..., description="Messages published to queue")
    messages_failed: int = Field(..., description="Failed message publications")
    
    # Amounts
    total_amount_cents: int = Field(..., description="Total amount in cents")
    
    # Timestamps
    created_at: datetime = Field(..., description="Job creation time")
    started_at: Optional[datetime] = Field(None, description="Processing start time")
    completed_at: Optional[datetime] = Field(None, description="Processing completion time")
    
    # Retry information
    retry_count: int = Field(..., description="Number of retries")
    
    # Error information
    error_message: Optional[str] = Field(None, description="Error message if failed")


class ConversionErrorResponse(BaseModel):
    """Response model for conversion errors."""
    
    error_id: str = Field(..., description="Error identifier")
    job_id: str = Field(..., description="Associated job ID")
    error_type: str = Field(..., description="Type of error")
    error_message: str = Field(..., description="Error message")
    record_type: Optional[str] = Field(None, description="ACH record type")
    line_number: Optional[int] = Field(None, description="Line number in file")
    severity: str = Field(..., description="Error severity")
    created_at: datetime = Field(..., description="Error timestamp")


class JobErrorsResponse(BaseModel):
    """Response model for job errors."""
    
    job_id: str = Field(..., description="Job identifier")
    total_errors: int = Field(..., description="Total number of errors")
    errors: List[ConversionErrorResponse] = Field(..., description="List of errors")


class JobListResponse(BaseModel):
    """Response model for job list."""
    
    total: int = Field(..., description="Total number of jobs")
    page: int = Field(..., description="Current page")
    page_size: int = Field(..., description="Page size")
    jobs: List[JobStatusResponse] = Field(..., description="List of jobs")


class RetryJobRequest(BaseModel):
    """Request model for job retry."""
    
    force: bool = Field(False, description="Force retry even if max retries exceeded")


class RetryJobResponse(BaseModel):
    """Response model for job retry."""
    
    job_id: str = Field(..., description="Job identifier")
    status: str = Field(..., description="New job status")
    retry_count: int = Field(..., description="Current retry count")
    message: str = Field(..., description="Retry message")


class HealthStatusResponse(BaseModel):
    """Response model for health status."""
    
    status: str = Field(..., description="Service status (UP/DOWN)")
    service: str = Field(..., description="Service name")
    version: str = Field(..., description="Service version")
    timestamp: datetime = Field(..., description="Status check timestamp")
    
    # Component health
    database: str = Field(..., description="Database status")
    message_queue: str = Field(..., description="Message queue status")
    
    # Additional info
    uptime_seconds: float = Field(..., description="Service uptime in seconds")


class HealthLivenessResponse(BaseModel):
    """Response model for liveness probe."""
    
    status: str = Field(..., description="Liveness status")
    timestamp: datetime = Field(..., description="Check timestamp")


class HealthReadinessResponse(BaseModel):
    """Response model for readiness probe."""
    
    status: str = Field(..., description="Readiness status")
    ready: bool = Field(..., description="Is service ready to accept traffic")
    timestamp: datetime = Field(..., description="Check timestamp")


class ErrorResponse(BaseModel):
    """Generic error response."""
    
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Additional details")
    request_id: Optional[str] = Field(None, description="Request identifier")
