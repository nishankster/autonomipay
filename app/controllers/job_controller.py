"""
REST API controller for job status and management endpoints.
"""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.config.database import get_db_session
from app.models.database_models import ConversionJob, ConversionError
from app.models.schemas import (
    JobStatusResponse, JobErrorsResponse, ConversionErrorResponse,
    JobListResponse, RetryJobRequest, RetryJobResponse, ErrorResponse
)
from app.services.conversion_service import AchConversionService
from app.monitoring.audit_logger import AuditLogger

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/{job_id}",
    response_model=JobStatusResponse,
    responses={
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    }
)
async def get_job_status(
    job_id: str,
    db_session: AsyncSession = Depends(get_db_session)
) -> JobStatusResponse:
    """
    Get status of a conversion job.
    
    Args:
        job_id: Job identifier
        db_session: Database session
    
    Returns:
        JobStatusResponse: Job status information
    
    Raises:
        HTTPException: If job not found
    """
    try:
        # Query job
        result = await db_session.execute(
            select(ConversionJob).where(ConversionJob.id == job_id)
        )
        job = result.scalar_one_or_none()
        
        if not job:
            raise HTTPException(
                status_code=404,
                detail=f"Job {job_id} not found"
            )
        
        return JobStatusResponse(
            job_id=job.id,
            filename=job.filename,
            status=job.status.value,
            total_entries=job.total_entries,
            successful_entries=job.successful_entries,
            failed_entries=job.failed_entries,
            messages_published=job.messages_published,
            messages_failed=job.messages_failed,
            total_amount_cents=job.total_amount_cents,
            created_at=job.created_at,
            started_at=job.started_at,
            completed_at=job.completed_at,
            retry_count=job.retry_count,
            error_message=job.error_message
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving job status: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )


@router.get(
    "/{job_id}/errors",
    response_model=JobErrorsResponse,
    responses={
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    }
)
async def get_job_errors(
    job_id: str,
    db_session: AsyncSession = Depends(get_db_session)
) -> JobErrorsResponse:
    """
    Get errors for a conversion job.
    
    Args:
        job_id: Job identifier
        db_session: Database session
    
    Returns:
        JobErrorsResponse: List of errors
    
    Raises:
        HTTPException: If job not found
    """
    try:
        # Verify job exists
        result = await db_session.execute(
            select(ConversionJob).where(ConversionJob.id == job_id)
        )
        job = result.scalar_one_or_none()
        
        if not job:
            raise HTTPException(
                status_code=404,
                detail=f"Job {job_id} not found"
            )
        
        # Query errors
        result = await db_session.execute(
            select(ConversionError).where(ConversionError.job_id == job_id)
        )
        errors = result.scalars().all()
        
        error_responses = [
            ConversionErrorResponse(
                error_id=error.id,
                job_id=error.job_id,
                error_type=error.error_type,
                error_message=error.error_message,
                record_type=error.record_type,
                line_number=error.line_number,
                severity=error.severity,
                created_at=error.created_at
            )
            for error in errors
        ]
        
        return JobErrorsResponse(
            job_id=job_id,
            total_errors=len(error_responses),
            errors=error_responses
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving job errors: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )


@router.get(
    "",
    response_model=JobListResponse,
    responses={
        500: {"model": ErrorResponse}
    }
)
async def list_jobs(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    status: Optional[str] = Query(None),
    db_session: AsyncSession = Depends(get_db_session)
) -> JobListResponse:
    """
    List conversion jobs with pagination.
    
    Args:
        page: Page number (1-indexed)
        page_size: Number of items per page
        status: Optional status filter
        db_session: Database session
    
    Returns:
        JobListResponse: List of jobs
    """
    try:
        # Build query
        query = select(ConversionJob)
        
        if status:
            query = query.where(ConversionJob.status == status)
        
        # Get total count
        count_result = await db_session.execute(
            select(ConversionJob).where(
                ConversionJob.status == status if status else True
            )
        )
        total = len(count_result.scalars().all())
        
        # Get paginated results
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)
        query = query.order_by(ConversionJob.created_at.desc())
        
        result = await db_session.execute(query)
        jobs = result.scalars().all()
        
        job_responses = [
            JobStatusResponse(
                job_id=job.id,
                filename=job.filename,
                status=job.status.value,
                total_entries=job.total_entries,
                successful_entries=job.successful_entries,
                failed_entries=job.failed_entries,
                messages_published=job.messages_published,
                messages_failed=job.messages_failed,
                total_amount_cents=job.total_amount_cents,
                created_at=job.created_at,
                started_at=job.started_at,
                completed_at=job.completed_at,
                retry_count=job.retry_count,
                error_message=job.error_message
            )
            for job in jobs
        ]
        
        return JobListResponse(
            total=total,
            page=page,
            page_size=page_size,
            jobs=job_responses
        )
        
    except Exception as e:
        logger.error(f"Error listing jobs: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )


@router.post(
    "/{job_id}/retry",
    response_model=RetryJobResponse,
    responses={
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    }
)
async def retry_job(
    job_id: str,
    request: RetryJobRequest,
    db_session: AsyncSession = Depends(get_db_session)
) -> RetryJobResponse:
    """
    Retry a failed conversion job.
    
    Args:
        job_id: Job identifier
        request: Retry request
        db_session: Database session
    
    Returns:
        RetryJobResponse: Retry status
    
    Raises:
        HTTPException: If job not found or retry fails
    """
    try:
        # Verify job exists
        result = await db_session.execute(
            select(ConversionJob).where(ConversionJob.id == job_id)
        )
        job = result.scalar_one_or_none()
        
        if not job:
            raise HTTPException(
                status_code=404,
                detail=f"Job {job_id} not found"
            )
        
        # Attempt retry
        conversion_service = AchConversionService(db_session)
        success = await conversion_service.retry_job(
            job_id=job_id,
            force=request.force
        )
        
        if not success:
            raise HTTPException(
                status_code=400,
                detail="Retry failed - job may have exceeded max retries"
            )
        
        # Log retry
        AuditLogger.log_job_retry(job_id=job_id, retry_count=job.retry_count)
        
        return RetryJobResponse(
            job_id=job_id,
            status="RETRYING",
            retry_count=job.retry_count,
            message="Job retry started"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrying job: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )
