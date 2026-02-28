"""
ACH conversion orchestration service.

This service coordinates the entire conversion workflow:
parsing ACH files, building RTP messages, and publishing to queue.
"""

import logging
import asyncio
from typing import Optional
from datetime import datetime
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ach_models import AchFile
from app.models.database_models import ConversionJob, ConversionError, JobStatus
from app.parsers.ach_parser import AchFileParser
from app.services.rtp_message_builder import RtpMessageBuilder
from app.config.message_queue import publish_message
from app.exceptions import AchParsingException, RtpMessageException, PublishingException

logger = logging.getLogger(__name__)


class AchConversionService:
    """Service for converting ACH files to RTP messages."""
    
    def __init__(self, db_session: AsyncSession):
        """
        Initialize conversion service.
        
        Args:
            db_session: Database session
        """
        self.db_session = db_session
    
    async def process_ach_file(
        self,
        file_content: str,
        filename: str,
        source_system: Optional[str] = None,
        correlation_id: Optional[str] = None
    ) -> str:
        """
        Process ACH file and convert to RTP messages.
        
        Args:
            file_content: Content of ACH file
            filename: Name of file
            source_system: Optional source system identifier
            correlation_id: Optional correlation ID
        
        Returns:
            str: Job ID
        
        Raises:
            AchParsingException: If parsing fails
            PublishingException: If publishing fails
        """
        job_id = str(uuid.uuid4())
        
        try:
            logger.info(f"Starting conversion job {job_id} for file {filename}")
            
            # Create job record
            job = ConversionJob(
                id=job_id,
                filename=filename,
                status=JobStatus.PROCESSING,
                file_size=len(file_content),
                source_system=source_system,
                correlation_id=correlation_id,
                started_at=datetime.utcnow()
            )
            self.db_session.add(job)
            await self.db_session.flush()
            
            # Parse ACH file
            logger.info(f"Parsing ACH file for job {job_id}")
            ach_file = await AchFileParser.parse_file(file_content, filename)
            
            # Update job with file statistics
            job.total_entries = ach_file.total_entries
            job.total_batches = len(ach_file.batches)
            job.total_amount_cents = ach_file.total_credit_amount
            
            # Process each entry and convert to RTP message
            successful_count = 0
            failed_count = 0
            
            for batch_idx, batch in enumerate(ach_file.batches):
                for entry_idx, entry in enumerate(batch.entries):
                    try:
                        # Build RTP message
                        rtp_message = RtpMessageBuilder.build_rtp_message(
                            entry=entry,
                            file_header=ach_file.file_header,
                            batch_header=batch.batch_header,
                            message_id=str(uuid.uuid4())
                        )
                        
                        # Publish to message queue
                        success = await publish_message(
                            message_body=rtp_message,
                            headers={
                                "job_id": job_id,
                                "entry_number": str(entry_idx),
                                "batch_number": str(batch_idx),
                                "correlation_id": correlation_id or job_id,
                                "source_system": source_system or "unknown"
                            }
                        )
                        
                        if success:
                            successful_count += 1
                            job.messages_published += 1
                            logger.debug(
                                f"Published RTP message for entry {entry.trace_number}"
                            )
                        else:
                            failed_count += 1
                            job.messages_failed += 1
                            
                            # Log error
                            error = ConversionError(
                                id=str(uuid.uuid4()),
                                job_id=job_id,
                                error_type="PublishingError",
                                error_message="Failed to publish message to queue",
                                record_type="6",
                                entry_number=entry_idx,
                                severity="ERROR"
                            )
                            self.db_session.add(error)
                            
                    except RtpMessageException as e:
                        failed_count += 1
                        job.messages_failed += 1
                        
                        # Log error
                        error = ConversionError(
                            id=str(uuid.uuid4()),
                            job_id=job_id,
                            error_type="RtpMessageError",
                            error_message=str(e),
                            record_type="6",
                            entry_number=entry_idx,
                            severity="ERROR"
                        )
                        self.db_session.add(error)
                        logger.error(f"Failed to build RTP message: {str(e)}")
                        
                    except Exception as e:
                        failed_count += 1
                        job.messages_failed += 1
                        
                        # Log error
                        error = ConversionError(
                            id=str(uuid.uuid4()),
                            job_id=job_id,
                            error_type="UnexpectedError",
                            error_message=str(e),
                            record_type="6",
                            entry_number=entry_idx,
                            severity="ERROR"
                        )
                        self.db_session.add(error)
                        logger.error(f"Unexpected error processing entry: {str(e)}")
            
            # Update job status
            job.successful_entries = successful_count
            job.failed_entries = failed_count
            job.completed_at = datetime.utcnow()
            
            if failed_count == 0:
                job.status = JobStatus.COMPLETED
                logger.info(
                    f"Job {job_id} completed successfully: "
                    f"{successful_count} entries processed"
                )
            elif successful_count == 0:
                job.status = JobStatus.FAILED
                job.error_message = f"All {failed_count} entries failed to process"
                logger.error(f"Job {job_id} failed: all entries failed")
            else:
                job.status = JobStatus.COMPLETED
                logger.warning(
                    f"Job {job_id} partially completed: "
                    f"{successful_count} succeeded, {failed_count} failed"
                )
            
            # Commit changes
            await self.db_session.commit()
            
            return job_id
            
        except AchParsingException as e:
            logger.error(f"ACH parsing failed for job {job_id}: {str(e)}")
            
            # Update job status
            job.status = JobStatus.FAILED
            job.error_message = str(e)
            job.completed_at = datetime.utcnow()
            
            # Log error
            error = ConversionError(
                id=str(uuid.uuid4()),
                job_id=job_id,
                error_type="AchParsingError",
                error_message=str(e),
                severity="CRITICAL"
            )
            self.db_session.add(error)
            
            await self.db_session.commit()
            raise
            
        except Exception as e:
            logger.error(f"Unexpected error in conversion job {job_id}: {str(e)}")
            
            # Update job status
            job.status = JobStatus.FAILED
            job.error_message = f"Unexpected error: {str(e)}"
            job.completed_at = datetime.utcnow()
            
            # Log error
            error = ConversionError(
                id=str(uuid.uuid4()),
                job_id=job_id,
                error_type="UnexpectedError",
                error_message=str(e),
                severity="CRITICAL"
            )
            self.db_session.add(error)
            
            await self.db_session.commit()
            raise
    
    async def retry_job(
        self,
        job_id: str,
        force: bool = False
    ) -> bool:
        """
        Retry a failed conversion job.
        
        Args:
            job_id: Job ID to retry
            force: Force retry even if max retries exceeded
        
        Returns:
            bool: True if retry started, False otherwise
        """
        try:
            # Get job from database
            from sqlalchemy import select
            
            result = await self.db_session.execute(
                select(ConversionJob).where(ConversionJob.id == job_id)
            )
            job = result.scalar_one_or_none()
            
            if not job:
                logger.error(f"Job {job_id} not found")
                return False
            
            # Check retry limit
            if job.retry_count >= job.max_retries and not force:
                logger.warning(
                    f"Job {job_id} has exceeded max retries ({job.max_retries})"
                )
                return False
            
            # Update job status
            job.status = JobStatus.RETRYING
            job.retry_count += 1
            job.started_at = datetime.utcnow()
            job.completed_at = None
            job.error_message = None
            
            await self.db_session.commit()
            
            logger.info(f"Retry started for job {job_id} (attempt {job.retry_count})")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to retry job {job_id}: {str(e)}")
            return False
