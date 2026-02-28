"""
REST API controller for health check endpoints.
"""

import logging
from datetime import datetime
import time

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.config.database import get_db_session
from app.config.message_queue import get_connection, get_channel
from app.models.schemas import (
    HealthStatusResponse, HealthLivenessResponse, HealthReadinessResponse
)

logger = logging.getLogger(__name__)

router = APIRouter()

# Track start time
start_time = time.time()


@router.get("/status", response_model=HealthStatusResponse)
async def health_status(
    db_session: AsyncSession = Depends(get_db_session)
) -> HealthStatusResponse:
    """
    Get comprehensive health status.
    
    Args:
        db_session: Database session
    
    Returns:
        HealthStatusResponse: Health status information
    """
    try:
        # Check database
        db_status = "UP"
        try:
            await db_session.execute(text("SELECT 1"))
        except Exception as e:
            logger.error(f"Database health check failed: {str(e)}")
            db_status = "DOWN"
        
        # Check message queue
        mq_status = "UP"
        try:
            connection = await get_connection()
            channel = await get_channel()
            if not connection or not channel:
                mq_status = "DOWN"
        except Exception as e:
            logger.error(f"Message queue health check failed: {str(e)}")
            mq_status = "DOWN"
        
        # Calculate uptime
        uptime_seconds = time.time() - start_time
        
        # Determine overall status
        overall_status = "UP" if db_status == "UP" and mq_status == "UP" else "DEGRADED"
        
        return HealthStatusResponse(
            status=overall_status,
            service="ach-to-rtp-service",
            version="1.0.0",
            timestamp=datetime.utcnow(),
            database=db_status,
            message_queue=mq_status,
            uptime_seconds=uptime_seconds
        )
        
    except Exception as e:
        logger.error(f"Health status check failed: {str(e)}")
        return HealthStatusResponse(
            status="DOWN",
            service="ach-to-rtp-service",
            version="1.0.0",
            timestamp=datetime.utcnow(),
            database="UNKNOWN",
            message_queue="UNKNOWN",
            uptime_seconds=time.time() - start_time
        )


@router.get("/live", response_model=HealthLivenessResponse)
async def health_live() -> HealthLivenessResponse:
    """
    Kubernetes liveness probe endpoint.
    
    Returns:
        HealthLivenessResponse: Liveness status
    """
    return HealthLivenessResponse(
        status="UP",
        timestamp=datetime.utcnow()
    )


@router.get("/ready", response_model=HealthReadinessResponse)
async def health_ready(
    db_session: AsyncSession = Depends(get_db_session)
) -> HealthReadinessResponse:
    """
    Kubernetes readiness probe endpoint.
    
    Args:
        db_session: Database session
    
    Returns:
        HealthReadinessResponse: Readiness status
    """
    try:
        # Check database
        await db_session.execute(text("SELECT 1"))
        
        # Check message queue
        connection = await get_connection()
        channel = await get_channel()
        
        if connection and channel:
            return HealthReadinessResponse(
                status="UP",
                ready=True,
                timestamp=datetime.utcnow()
            )
        else:
            return HealthReadinessResponse(
                status="DOWN",
                ready=False,
                timestamp=datetime.utcnow()
            )
            
    except Exception as e:
        logger.error(f"Readiness check failed: {str(e)}")
        return HealthReadinessResponse(
            status="DOWN",
            ready=False,
            timestamp=datetime.utcnow()
        )
