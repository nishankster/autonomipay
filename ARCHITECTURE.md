# Architecture Documentation

## System Overview

The ACH to RTP Conversion Service is a production-grade microservice that converts NACHA ACH files into ISO 20022 RTP (pacs.008) messages and publishes them asynchronously to an RTP gateway via message queue.

```
┌─────────────────────────────────────────────────────────────────┐
│                         Client Applications                      │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    REST API Layer (Port 8080)                    │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ FileUploadController │ HealthCheckController │ StatusCtrl │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Service Layer                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ AchConversionService │ RtpMessageBuilderService          │  │
│  │ MessagePublisherService                                  │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        ▼                ▼                ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ ACH Parser   │  │ RTP Builder  │  │ MQ Publisher │
└──────────────┘  └──────────────┘  └──────────────┘
        │                │                │
        ▼                ▼                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Data Persistence Layer                        │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ PostgreSQL Database │ RabbitMQ Message Queue             │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Component Architecture

### 1. REST API Layer

**Responsibility:** Handle HTTP requests and responses

**Components:**
- `FileUploadController`: Handles ACH file uploads
- `HealthCheckController`: Provides health check endpoints
- `ConversionStatusController`: Tracks conversion job status
- `GlobalExceptionHandler`: Centralized error handling

**Key Features:**
- Multipart file upload support
- CORS enabled for cross-origin requests
- Comprehensive error responses
- Health check probes for Kubernetes

### 2. Service Layer

**Responsibility:** Orchestrate business logic

**Components:**
- `AchConversionService`: Main orchestration service
  - Coordinates parsing, conversion, and publishing
  - Tracks conversion statistics
  - Handles batch processing

- `RtpMessageBuilderService`: Generates ISO 20022 messages
  - Converts ACH fields to RTP format
  - Validates required fields
  - Escapes XML special characters

- `MessagePublisherService`: Publishes to message queue
  - Sends messages to RabbitMQ
  - Handles connection errors
  - Determines retry eligibility

### 3. Parser Layer

**Responsibility:** Parse and validate ACH files

**Components:**
- `AchFileParser`: Main parser class
  - Reads fixed-width NACHA records
  - Validates record structure
  - Builds domain objects

- `AchFieldExtractor`: Utility for field extraction
  - Extracts string, numeric, date, time fields
  - Validates field values
  - Handles parsing errors

**Supported Record Types:**
- Type 1: File Header
- Type 5: Batch Header
- Type 6: Entry Detail
- Type 7: Addenda
- Type 8: Batch Control
- Type 9: File Control

### 4. Builder Layer

**Responsibility:** Generate ISO 20022 RTP messages

**Components:**
- `RtpMessageBuilderService`: Builds pacs.008 messages
  - Creates XML structure
  - Maps ACH fields to RTP fields
  - Validates message content

**Output Format:** ISO 20022 pacs.008 XML

### 5. Publisher Layer

**Responsibility:** Publish messages to queue

**Components:**
- `MessagePublisherService`: RabbitMQ publisher
  - Sends messages with headers
  - Handles connection errors
  - Determines retry strategy

**Message Queue:** RabbitMQ with dead-letter queue support

### 6. Monitoring Layer

**Responsibility:** Collect metrics and audit logs

**Components:**
- `MetricsCollector`: Collects application metrics
  - File upload counters
  - Entry processing counters
  - Message generation/publishing timers

- `AuditLogger`: Records compliance events
  - File uploads
  - Message generation
  - Error events
  - Security events

## Data Models

### ACH Domain Models

```
AchFile
├── AchFileHeader
├── AchBatch[]
│   ├── AchBatchHeader
│   ├── AchEntry[]
│   │   └── AchAddenda[]
│   └── AchBatchControl
└── AchFileControl
```

**Key Classes:**
- `AchFile`: Complete ACH file
- `AchBatch`: Collection of entries
- `AchEntry`: Individual transaction
- `AchAddenda`: Additional transaction info

### RTP Message Format

ISO 20022 pacs.008 XML structure:
```xml
<Document>
  <CstmrCdtTrfInitn>
    <GrpHdr>...</GrpHdr>
    <PmtInf>
      <CdtTrfTxInf>...</CdtTrfTxInf>
    </PmtInf>
  </CstmrCdtTrfInitn>
</Document>
```

## Field Mapping: ACH to RTP

| ACH Field | Record Type | RTP Field | pacs.008 Path |
|-----------|------------|-----------|---------------|
| Originating Bank | File Header | Debtor Agent | PmtInf/DebtorAgt |
| Effective Date | Batch Header | Payment Date | PmtInf/CreDtTm |
| Receiving DFI | Entry Detail | Creditor Agent | CdtTrfTxInf/CdtrAgt |
| Account Number | Entry Detail | Creditor Account | CdtTrfTxInf/CdtrAcct |
| Amount | Entry Detail | Transaction Amount | CdtTrfTxInf/Amt |
| Individual Name | Entry Detail | Creditor Name | CdtTrfTxInf/Cdtr/Nm |
| Addenda Records | Addenda | Remittance Info | CdtTrfTxInf/RmtInf |

## Error Handling Strategy

### Exception Hierarchy

```
Exception
├── AchParsingException
│   ├── Invalid record format
│   ├── Field extraction errors
│   └── Validation failures
├── RtpMessageException
│   ├── Missing required fields
│   ├── Invalid field values
│   └── Schema validation errors
├── PublishingException
│   ├── Connection errors (retryable)
│   ├── Authentication errors (non-retryable)
│   └── Queue errors
└── ValidationException
    ├── Field validation
    └── Business rule violations
```

### Error Recovery

1. **Parsing Errors**: Log and skip entry
2. **Message Generation Errors**: Log and mark as failed
3. **Publishing Errors**: Retry with exponential backoff
4. **Validation Errors**: Return detailed error message

## Asynchronous Processing

### Message Flow

```
1. File Upload
   ↓
2. Parse ACH File
   ↓
3. For Each Entry:
   ├─ Generate RTP Message
   ├─ Validate Message
   └─ Publish to Queue
   ↓
4. Return Conversion Result
```

### Async Features

- Non-blocking file upload
- Batch entry processing
- Async message publishing
- Configurable retry policy

## Database Schema

### Planned Tables (for future versions)

```sql
-- Conversion Jobs
CREATE TABLE conversion_jobs (
  id UUID PRIMARY KEY,
  file_name VARCHAR(255),
  status VARCHAR(50),
  total_entries INT,
  successful_conversions INT,
  failed_conversions INT,
  created_at TIMESTAMP,
  completed_at TIMESTAMP
);

-- Entry Errors
CREATE TABLE entry_errors (
  id UUID PRIMARY KEY,
  job_id UUID REFERENCES conversion_jobs,
  entry_id VARCHAR(255),
  error_message TEXT,
  created_at TIMESTAMP
);

-- Published Messages
CREATE TABLE published_messages (
  id UUID PRIMARY KEY,
  job_id UUID REFERENCES conversion_jobs,
  entry_id VARCHAR(255),
  message_id VARCHAR(255),
  status VARCHAR(50),
  published_at TIMESTAMP
);
```

## Configuration Management

### Environment-Specific Profiles

- **dev**: Local development with verbose logging
- **prod**: Production with optimized settings

### Configuration Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `ach.max-file-size` | 10485760 | Maximum file size (bytes) |
| `ach.max-entries-per-batch` | 10000 | Max entries per batch |
| `rtp.message-timeout-ms` | 30000 | Message generation timeout |
| `mq.exchange-name` | rtp-gateway | RabbitMQ exchange |
| `mq.routing-key` | rtp.credit.transfer | RabbitMQ routing key |
| `mq.retry-max-attempts` | 3 | Max retry attempts |

## Monitoring and Observability

### Metrics

**Counters:**
- `ach.file.uploads.total`: Total file uploads
- `ach.entries.processed.total`: Total entries processed
- `rtp.messages.published.total`: Total messages published

**Timers:**
- `ach.file.parsing.duration`: File parsing latency
- `rtp.message.generation.duration`: Message generation latency
- `rtp.message.publishing.duration`: Publishing latency

### Logging

**Log Levels:**
- `DEBUG`: Detailed operation logs
- `INFO`: General application events
- `WARN`: Warning conditions
- `ERROR`: Error conditions

**Log Files:**
- `ach-to-rtp-service.log`: Application logs
- `audit.log`: Compliance audit logs

### Health Checks

- **Liveness Probe**: `/api/v1/health/live`
- **Readiness Probe**: `/api/v1/health/ready`
- **Status Endpoint**: `/api/v1/health/status`

## Deployment Architecture

### Docker

- Multi-stage build for optimized image size
- Non-root user for security
- Health checks configured
- Alpine base image for minimal footprint

### Kubernetes

- StatelessReplicaSet deployment
- Service for load balancing
- ConfigMap for configuration
- Secrets for credentials
- HPA for auto-scaling
- PDB for high availability

## Security Considerations

### Current Implementation

- No authentication (add OAuth2 in production)
- No rate limiting (add in production)
- No encryption (add TLS in production)
- Non-root container user

### Recommended Enhancements

1. **Authentication**: OAuth2 / API Key
2. **Authorization**: RBAC for different user roles
3. **Encryption**: TLS for data in transit
4. **Secrets Management**: HashiCorp Vault
5. **Rate Limiting**: Token bucket algorithm
6. **Input Validation**: Comprehensive validation
7. **Audit Logging**: Detailed compliance logs

## Performance Considerations

### Optimization Strategies

1. **Connection Pooling**: HikariCP for database
2. **Async Processing**: Spring @Async for non-blocking operations
3. **Batch Processing**: Process multiple entries efficiently
4. **Caching**: Cache frequently accessed data
5. **Message Compression**: Compress large messages
6. **Lazy Loading**: Load data on demand

### Scalability

- Horizontal scaling via Kubernetes
- Load balancing across replicas
- Database connection pooling
- Message queue buffering

## Disaster Recovery

### Backup Strategy

- Daily database backups
- Message queue persistence
- Log archival

### Recovery Procedures

- Database restore from backup
- Message replay from queue
- Service restart procedures

## Future Enhancements

1. **Database Persistence**: Store conversion history
2. **Job Tracking**: Track long-running jobs
3. **Retry Logic**: Implement sophisticated retry strategy
4. **Webhook Notifications**: Notify on job completion
5. **API Authentication**: Secure API endpoints
6. **Rate Limiting**: Prevent abuse
7. **Caching**: Improve performance
8. **Multi-tenancy**: Support multiple customers
9. **Kafka Support**: Alternative to RabbitMQ
10. **GraphQL API**: Modern API interface

## References

- [Spring Boot Architecture Best Practices](https://spring.io/guides)
- [Microservices Architecture](https://microservices.io/)
- [NACHA ACH Format](https://www.nacha.org/)
- [ISO 20022 Standard](https://www.iso20022.org/)
- [Kubernetes Architecture](https://kubernetes.io/docs/concepts/architecture/)
- [RabbitMQ Best Practices](https://www.rabbitmq.com/best-practices.html)
