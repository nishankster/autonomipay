"""
REST API controller for ACH file conversion endpoints.
"""

import logging
from typing import Optional

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.database import get_db_session
from app.models.schemas import FileUploadResponse, ErrorResponse
from app.services.conversion_service import AchConversionService
from app.exceptions import AchParsingException, PublishingException
from app.monitoring.audit_logger import AuditLogger

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/upload",
    response_model=FileUploadResponse,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    }
)
async def upload_ach_file(
    file: UploadFile = File(...),
    source_system: Optional[str] = Query(None),
    correlation_id: Optional[str] = Query(None),
    db_session: AsyncSession = Depends(get_db_session)
) -> FileUploadResponse:
    """
    Upload and convert ACH file to RTP messages.
    
    Args:
        file: ACH file to upload
        source_system: Optional source system identifier
        correlation_id: Optional correlation ID for tracking
        db_session: Database session
    
    Returns:
        FileUploadResponse: Job information
    
    Raises:
        HTTPException: If upload or processing fails
    """
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(
                status_code=400,
                detail="Filename is required"
            )
        
        if not file.filename.endswith('.ach'):
            logger.warning(f"File {file.filename} does not have .ach extension")
        
        # Read file content
        content = await file.read()
        
        if not content:
            raise HTTPException(
                status_code=400,
                detail="File is empty"
            )
        
        # Decode content
        try:
            file_content = content.decode('utf-8')
        except UnicodeDecodeError:
            raise HTTPException(
                status_code=400,
                detail="File must be UTF-8 encoded"
            )
        
        # Log file upload
        AuditLogger.log_file_upload(
            filename=file.filename,
            file_size=len(content),
            job_id="pending",  # Will be assigned by service
            source_system=source_system
        )
        
        # Process file
        conversion_service = AchConversionService(db_session)
        job_id = await conversion_service.process_ach_file(
            file_content=file_content,
            filename=file.filename,
            source_system=source_system,
            correlation_id=correlation_id
        )
        
        logger.info(f"File {file.filename} processed successfully, job_id: {job_id}")
        
        return FileUploadResponse(
            job_id=job_id,
            filename=file.filename,
            status="PROCESSING",
            created_at=None  # Would be populated from DB
        )
        
    except AchParsingException as e:
        logger.error(f"ACH parsing error: {str(e)}")
        AuditLogger.log_conversion_failure(
            job_id="unknown",
            error_message=str(e),
            error_type="AchParsingException"
        )
        raise HTTPException(
            status_code=400,
            detail=f"ACH parsing error: {str(e)}"
        )
        
    except PublishingException as e:
        logger.error(f"Message publishing error: {str(e)}")
        AuditLogger.log_queue_error(
            operation="publish",
            error_message=str(e)
        )
        raise HTTPException(
            status_code=500,
            detail=f"Message publishing error: {str(e)}"
        )
        
    except HTTPException:
        raise
        
    except Exception as e:
        logger.error(f"Unexpected error during file upload: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )
