"""
ACH to RTP Conversion Service - Main Application Entry Point

This module initializes the FastAPI application with all routes,
middleware, and startup/shutdown handlers.
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config.settings import Settings
from app.config.database import init_db, close_db
from app.config.message_queue import init_mq, close_mq
from app.controllers.health_controller import router as health_router
from app.controllers.conversion_controller import router as conversion_router
from app.controllers.job_controller import router as job_router
from app.monitoring.metrics import setup_metrics
from app.monitoring.audit_logger import setup_audit_logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

settings = Settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """
    Manage application lifecycle - startup and shutdown events.
    
    Yields:
        None
    """
    # Startup
    logger.info("Starting ACH to RTP Conversion Service")
    
    try:
        # Initialize database
        await init_db()
        logger.info("Database initialized successfully")
        
        # Initialize message queue
        await init_mq()
        logger.info("Message queue initialized successfully")
        
        # Setup metrics
        setup_metrics()
        logger.info("Metrics collection initialized")
        
        # Setup audit logging
        setup_audit_logging()
        logger.info("Audit logging initialized")
        
    except Exception as e:
        logger.error(f"Failed to initialize application: {str(e)}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down ACH to RTP Conversion Service")
    
    try:
        # Close message queue
        await close_mq()
        logger.info("Message queue closed")
        
        # Close database
        await close_db()
        logger.info("Database closed")
        
    except Exception as e:
        logger.error(f"Error during shutdown: {str(e)}")


# Create FastAPI application
app = FastAPI(
    title="ACH to RTP Conversion Service",
    description="Convert NACHA ACH files to ISO 20022 RTP messages",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handlers
@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions."""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc) if settings.DEBUG else "An error occurred"
        }
    )


# Include routers
app.include_router(health_router, prefix="/api/v1/health", tags=["Health"])
app.include_router(conversion_router, prefix="/api/v1/conversion", tags=["Conversion"])
app.include_router(job_router, prefix="/api/v1/jobs", tags=["Jobs"])


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint."""
    return {
        "service": "ach-to-rtp-service",
        "version": "1.0.0",
        "status": "running"
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
