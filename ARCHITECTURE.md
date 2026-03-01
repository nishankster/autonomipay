# ACH to RTP Conversion Service - Architecture Guide

This document describes the system architecture, design patterns, and implementation details of the ACH to RTP Conversion Service.

## Table of Contents

1. [System Overview](#system-overview)
2. [Technology Stack](#technology-stack)
3. [Architecture Layers](#architecture-layers)
4. [Data Flow](#data-flow)
5. [Component Details](#component-details)
6. [Design Patterns](#design-patterns)
7. [Scalability](#scalability)
8. [Reliability](#reliability)

---

## System Overview

The ACH to RTP Conversion Service is a production-grade microservice that converts NACHA ACH files to ISO 20022 RTP messages. The service follows a layered architecture with clear separation of concerns.

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│                    REST API Layer                        │
│  (FastAPI, Pydantic, OpenAPI Documentation)             │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│                 Controllers Layer                        │
│  (Request handling, validation, response formatting)    │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│                  Services Layer                          │
│  (Business logic, ACH parsing, RTP generation)          │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│              Data Access Layer                           │
│  (SQLAlchemy ORM, async database operations)            │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│         External Services Layer                          │
│  (PostgreSQL, RabbitMQ, Message Publishing)             │
└─────────────────────────────────────────────────────────┘
```

---

## Technology Stack

### Core Framework

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **Web Framework** | FastAPI | 0.104+ | Modern async web framework |
| **ASGI Server** | Uvicorn | 0.24+ | ASGI application server |
| **Type Validation** | Pydantic | 2.5+ | Data validation and serialization |
| **Settings** | Pydantic Settings | 2.1+ | Environment configuration |

### Database

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **ORM** | SQLAlchemy | 2.0+ | Async object-relational mapping |
| **Driver** | asyncpg | 0.29+ | PostgreSQL async driver |
| **Database** | PostgreSQL | 13+ | Relational database |
| **Migrations** | Alembic | 1.13+ | Database schema management |

### Message Queue

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **Broker** | RabbitMQ | 3.10+ | Message queue broker |
| **Client** | aio-pika | 13.0+ | Async RabbitMQ client |
| **Protocol** | AMQP | 0.9.1 | Message protocol |

### Monitoring & Logging

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **Metrics** | Prometheus Client | 0.19+ | Metrics collection |
| **Logging** | Python JSON Logger | 2.0+ | Structured JSON logging |
| **Async Runtime** | asyncio | Built-in | Async I/O runtime |

---

## Architecture Layers

### 1. REST API Layer

**Location**: `app/controllers/`

The REST API layer handles HTTP requests and responses using FastAPI. Key responsibilities include request validation using Pydantic models, response formatting and serialization, error handling with proper HTTP status codes, and automatic OpenAPI documentation generation.

**Key Files**:

- `conversion_controller.py` - File upload endpoint
- `job_controller.py` - Job management endpoints
- `health_controller.py` - Health check endpoints

### 2. Controllers Layer

Controllers handle request routing and business logic orchestration. They validate input parameters, call appropriate services, handle exceptions and errors, and format responses.

### 3. Services Layer

**Location**: `app/services/`

Services contain core business logic for ACH parsing and RTP message generation.

**Key Services**:

| Service | Purpose |
|---------|---------|
| `AchConversionService` | Orchestrates ACH parsing and RTP generation |
| `RtpMessageBuilderService` | Builds ISO 20022 RTP messages |
| `MessagePublisherService` | Publishes messages to RabbitMQ |

### 4. Data Access Layer

**Location**: `app/config/database.py`

The data access layer provides async database operations using SQLAlchemy ORM with async database connections, connection pooling, transaction management, and query builders.

### 5. External Services Layer

**Location**: `app/config/`

External services handle integration with PostgreSQL and RabbitMQ for job tracking, error logging, audit trails, and asynchronous message publishing.

---

## Data Flow

### File Upload and Processing Flow

The complete flow from file upload to RTP message publishing follows these steps:

1. User uploads ACH file via REST API
2. FastAPI receives multipart/form-data request
3. Pydantic validates request parameters
4. Controller calls AchConversionService.process_ach_file()
5. ACH file is parsed by AchFileParser
6. Each entry is converted to RTP message by RtpMessageBuilderService
7. RTP messages are published to RabbitMQ
8. Job status is persisted to PostgreSQL
9. Response is returned to client with job_id
10. RTP gateway consumes messages from RabbitMQ queue

### Job Status Query Flow

When a client requests job status, the system retrieves the information from the database and returns it with current statistics.

### Error Handling Flow

Errors are caught, logged, persisted to the database, and the job status is updated to FAILED so clients can query error details.

---

## Component Details

### ACH Parser

**Location**: `app/parsers/ach_parser.py`

Parses NACHA ACH files according to the official specification. Supports all record types including file header, batch header, entry detail, addenda, batch control, and file control records.

**Key Features**:

- Fixed-width field extraction
- Validation of field formats
- Error reporting with line numbers
- Support for multiple batches and entries

### RTP Message Builder

**Location**: `app/services/rtp_message_builder.py`

Builds ISO 20022 pacs.008 XML messages from ACH entries with comprehensive field mapping between ACH and RTP formats.

### Message Publisher

**Location**: `app/config/message_queue.py`

Publishes RTP messages to RabbitMQ with reliability features including async message publishing, automatic retry on failure, dead-letter queue for failed messages, and message persistence.

---

## Design Patterns

### Dependency Injection

FastAPI's `Depends()` provides dependency injection for database sessions and services, making the code testable and maintainable.

### Repository Pattern

SQLAlchemy ORM acts as a repository, abstracting database queries and providing a clean interface for data access.

### Service Layer Pattern

Business logic is isolated in service classes, separating concerns and making the code more testable and reusable.

### Factory Pattern

Pydantic models act as factories for domain objects, providing type-safe object creation.

### Observer Pattern

Logging and monitoring observe application events, providing visibility into system behavior.

---

## Scalability

### Horizontal Scaling

The service is designed for horizontal scaling with stateless design, efficient connection pooling, non-blocking async I/O, and decoupled message queue processing.

Multiple instances can be deployed behind a load balancer, all sharing the same PostgreSQL database and RabbitMQ broker.

### Vertical Scaling

Increase resources for single instances by adding CPU, memory, and network bandwidth to improve processing speed and throughput.

### Database Optimization

Indexes on common query fields improve database performance significantly:

```sql
CREATE INDEX idx_job_status ON jobs(status);
CREATE INDEX idx_job_created_at ON jobs(created_at);
CREATE INDEX idx_error_job_id ON errors(job_id);
```

---

## Reliability

### Error Handling

Comprehensive error handling at all layers ensures graceful degradation and proper error reporting to clients.

### Retry Logic

Failed jobs can be retried with configurable retry limits and exponential backoff strategies.

### Dead-Letter Queue

Failed messages are sent to a dead-letter queue for manual review and recovery.

### Health Checks

Kubernetes probes monitor service health with liveness and readiness checks for proper orchestration.

### Monitoring

Prometheus metrics track service health, request latency, throughput, and error rates for observability.

---

## Security Considerations

### Input Validation

All inputs are validated using Pydantic with type checking and field constraints.

### Output Encoding

XML special characters are properly escaped to prevent injection attacks.

### Secrets Management

Sensitive data is stored in environment variables, never hardcoded in source code.

---

## Future Enhancements

Potential improvements include caching with Redis, webhook callbacks, batch APIs, analytics and reporting, enhanced audit trails, end-to-end encryption, rate limiting, and GraphQL API support.
