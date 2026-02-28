"""
Metrics collection and monitoring for the service.

This module provides Prometheus metrics for monitoring
application performance and health.
"""

import logging
from prometheus_client import Counter, Histogram, Gauge, CollectorRegistry

logger = logging.getLogger(__name__)

# Global registry
registry = CollectorRegistry()

# Counters
ach_files_uploaded_total = Counter(
    'ach_files_uploaded_total',
    'Total ACH files uploaded',
    registry=registry
)

ach_entries_processed_total = Counter(
    'ach_entries_processed_total',
    'Total ACH entries processed',
    ['status'],  # success, failure
    registry=registry
)

rtp_messages_published_total = Counter(
    'rtp_messages_published_total',
    'Total RTP messages published',
    ['status'],  # success, failure
    registry=registry
)

conversion_jobs_total = Counter(
    'conversion_jobs_total',
    'Total conversion jobs',
    ['status'],  # completed, failed, retrying
    registry=registry
)

# Histograms
file_upload_duration_seconds = Histogram(
    'file_upload_duration_seconds',
    'File upload duration in seconds',
    registry=registry
)

ach_parsing_duration_seconds = Histogram(
    'ach_parsing_duration_seconds',
    'ACH parsing duration in seconds',
    registry=registry
)

rtp_message_generation_duration_seconds = Histogram(
    'rtp_message_generation_duration_seconds',
    'RTP message generation duration in seconds',
    registry=registry
)

message_publishing_duration_seconds = Histogram(
    'message_publishing_duration_seconds',
    'Message publishing duration in seconds',
    registry=registry
)

conversion_job_duration_seconds = Histogram(
    'conversion_job_duration_seconds',
    'Conversion job duration in seconds',
    registry=registry
)

# Gauges
active_conversion_jobs = Gauge(
    'active_conversion_jobs',
    'Number of active conversion jobs',
    registry=registry
)

failed_conversion_jobs = Gauge(
    'failed_conversion_jobs',
    'Number of failed conversion jobs',
    registry=registry
)

pending_messages_in_queue = Gauge(
    'pending_messages_in_queue',
    'Number of pending messages in queue',
    registry=registry
)

database_connection_pool_size = Gauge(
    'database_connection_pool_size',
    'Database connection pool size',
    registry=registry
)

database_connection_pool_checked_out = Gauge(
    'database_connection_pool_checked_out',
    'Database connections checked out',
    registry=registry
)


def setup_metrics():
    """Initialize metrics collection."""
    logger.info("Metrics collection initialized")


def get_registry():
    """Get Prometheus metrics registry."""
    return registry
