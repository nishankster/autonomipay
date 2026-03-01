<<<<<<< HEAD
# ACH to RTP Conversion Service (Python/FastAPI)

A production-ready FastAPI microservice that converts NACHA ACH (Automated Clearing House) files to ISO 20022 RTP (Real-Time Payments) messages for asynchronous processing via message queues.

## 🎯 Features

- **ACH File Parsing**: Complete NACHA format support (records 1, 5, 6, 7, 8, 9)
- **RTP Message Generation**: ISO 20022 pacs.008 XML format for credit transfers
- **Async Processing**: Non-blocking file upload and conversion using FastAPI
- **Message Queue Integration**: RabbitMQ publisher with dead-letter queue support
- **Job Tracking**: Database persistence for job status, errors, and audit trails
- **REST API**: Comprehensive endpoints for upload, status, and error retrieval
- **Health Checks**: Kubernetes-ready liveness and readiness probes
- **Monitoring**: Prometheus metrics collection and structured JSON logging
- **Error Handling**: Detailed validation with granular error reporting
- **Retry Logic**: Configurable retry mechanism for failed jobs
- **Docker Ready**: Multi-stage builds and docker-compose for local development
- **Kubernetes Ready**: Deployment manifests with HPA, PDB, RBAC

## 📋 Prerequisites

- Python 3.11+
- PostgreSQL 13+
- RabbitMQ 3.10+
- Docker & Docker Compose (for containerized setup)

## 🚀 Quick Start

### Local Development

1. **Clone and setup**:
   ```bash
   cd /home/ubuntu/ach-to-rtp-service
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Start dependencies**:
   ```bash
   docker-compose up -d
   ```

3. **Run the service**:
   ```bash
   python -m uvicorn app.main:app --reload
   ```

4. **Access the service**:
   - API: http://localhost:8080
   - API Docs: http://localhost:8080/docs
   - RabbitMQ Management: http://localhost:15672 (guest/guest)
   - PostgreSQL: localhost:5432 (postgres/postgres)

### Docker Compose

```bash
docker-compose up --build
```

## 📚 API Endpoints

### File Upload
```
POST /api/v1/conversion/upload
Content-Type: multipart/form-data

Parameters:
  - file: ACH file (required)
  - source_system: Source identifier (optional)
  - correlation_id: Tracking ID (optional)

Response:
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "filename": "payroll.ach",
  "status": "PROCESSING",
  "created_at": "2024-01-15T10:30:00Z"
}
```

### Job Status
```
GET /api/v1/jobs/{job_id}

Response:
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "filename": "payroll.ach",
  "status": "COMPLETED",
  "total_entries": 100,
  "successful_entries": 98,
  "failed_entries": 2,
  "messages_published": 98,
  "messages_failed": 2,
  "total_amount_cents": 5000000,
  "created_at": "2024-01-15T10:30:00Z",
  "completed_at": "2024-01-15T10:35:00Z",
  "retry_count": 0,
  "error_message": null
}
```

### Job Errors
```
GET /api/v1/jobs/{job_id}/errors

Response:
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "total_errors": 2,
  "errors": [
    {
      "error_id": "err-001",
      "job_id": "550e8400-e29b-41d4-a716-446655440000",
      "error_type": "RtpMessageError",
      "error_message": "Individual name is required",
      "record_type": "6",
      "line_number": 5,
      "severity": "ERROR",
      "created_at": "2024-01-15T10:31:00Z"
    }
  ]
}
```

### List Jobs
```
GET /api/v1/jobs?page=1&page_size=10&status=COMPLETED

Response:
{
  "total": 42,
  "page": 1,
  "page_size": 10,
  "jobs": [...]
}
```

### Retry Job
```
POST /api/v1/jobs/{job_id}/retry

Request:
{
  "force": false
}

Response:
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "RETRYING",
  "retry_count": 1,
  "message": "Job retry started"
}
```

### Health Status
```
GET /api/v1/health/status

Response:
{
  "status": "UP",
  "service": "ach-to-rtp-service",
  "version": "1.0.0",
  "timestamp": "2024-01-15T10:30:00Z",
  "database": "UP",
  "message_queue": "UP",
  "uptime_seconds": 3600.5
}
```

### Liveness Probe
```
GET /api/v1/health/live
```

### Readiness Probe
```
GET /api/v1/health/ready
```

## 🏗️ Architecture

### Technology Stack

- **Framework**: FastAPI 0.104+
- **Language**: Python 3.11+
- **Async Runtime**: asyncio with uvicorn
- **Database**: PostgreSQL with SQLAlchemy async ORM
- **Message Queue**: RabbitMQ with aio-pika
- **Validation**: Pydantic v2
- **Containerization**: Docker
- **Orchestration**: Kubernetes

### Components

1. **ACH Parser** (`app/parsers/ach_parser.py`)
   - Parses NACHA fixed-width format
   - Validates record structure and field types
   - Extracts all record types (1, 5, 6, 7, 8, 9)

2. **RTP Message Builder** (`app/services/rtp_message_builder.py`)
   - Converts ACH entries to ISO 20022 pacs.008 XML
   - Performs field mapping and validation
   - Handles XML special character escaping

3. **Conversion Service** (`app/services/conversion_service.py`)
   - Orchestrates parsing and message generation
   - Manages job lifecycle and status tracking
   - Handles retry logic and error collection

4. **Message Publisher** (`app/config/message_queue.py`)
   - Async RabbitMQ integration using aio-pika
   - Dead-letter queue support for failed messages
   - Configurable retry policies

5. **REST API** (`app/controllers/`)
   - FastAPI endpoints for file upload and job management
   - Comprehensive error handling and validation
   - Structured response models with Pydantic

6. **Database** (`app/config/database.py`)
   - SQLAlchemy async ORM
   - PostgreSQL connection pooling
   - Job and error tracking tables

## 🔧 Configuration

### Environment Variables

```bash
# Application
APP_NAME=ACH to RTP Conversion Service
APP_VERSION=1.0.0
DEBUG=False
PORT=8080
HOST=0.0.0.0

# Database
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/ach_rtp_db
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=10

# RabbitMQ
RABBITMQ_HOST=localhost
RABBITMQ_PORT=5672
RABBITMQ_USERNAME=guest
RABBITMQ_PASSWORD=guest
RABBITMQ_EXCHANGE=rtp-gateway
RABBITMQ_ROUTING_KEY=rtp.credit.transfer

# ACH Processing
ACH_MAX_FILE_SIZE=10485760
ACH_MAX_ENTRIES_PER_BATCH=10000

# Job Processing
JOB_MAX_RETRIES=3
JOB_RETRY_DELAY_SECONDS=60

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
```

## 📦 Project Structure

```
ach-to-rtp-service/
├── app/
│   ├── main.py                 # FastAPI application entry point
│   ├── config/
│   │   ├── settings.py         # Configuration management
│   │   ├── database.py         # Database setup
│   │   └── message_queue.py    # RabbitMQ configuration
│   ├── models/
│   │   ├── ach_models.py       # ACH domain models
│   │   ├── database_models.py  # SQLAlchemy models
│   │   └── schemas.py          # Pydantic schemas
│   ├── parsers/
│   │   ├── ach_parser.py       # ACH file parser
│   │   └── ach_field_extractor.py  # Field extraction utility
│   ├── services/
│   │   ├── conversion_service.py   # Orchestration service
│   │   └── rtp_message_builder.py  # RTP message generation
│   ├── controllers/
│   │   ├── conversion_controller.py # File upload endpoints
│   │   ├── job_controller.py       # Job management endpoints
│   │   └── health_controller.py    # Health check endpoints
│   └── monitoring/
│       ├── metrics.py          # Prometheus metrics
│       └── audit_logger.py     # Audit logging
├── tests/
│   ├── test_ach_field_extractor.py
│   └── test_rtp_message_builder.py
├── k8s/
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── configmap.yaml
│   ├── secret.yaml
│   ├── rbac.yaml
│   ├── hpa.yaml
│   └── pdb.yaml
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
```

## 🧪 Testing

### Run Unit Tests
```bash
pytest tests/
```

### Run with Coverage
```bash
pytest --cov=app tests/
```

### Run Specific Test
```bash
pytest tests/test_ach_field_extractor.py -v
```

## 🐳 Docker

### Build Image
```bash
docker build -t ach-to-rtp-service:1.0.0 .
```

### Run Container
```bash
docker run -d \
  -p 8080:8080 \
  -e DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/ach_rtp_db \
  -e RABBITMQ_HOST=rabbitmq \
  ach-to-rtp-service:1.0.0
```

## ☸️ Kubernetes Deployment

### Prerequisites
```bash
kubectl create namespace ach-rtp
```

### Deploy
```bash
kubectl apply -f k8s/ -n ach-rtp
```

### Verify Deployment
```bash
kubectl get pods -n ach-rtp
kubectl logs -f deployment/ach-to-rtp-service -n ach-rtp
```

### Port Forward
```bash
kubectl port-forward svc/ach-to-rtp-service 8080:8080 -n ach-rtp
```

## 📊 Monitoring

### Prometheus Metrics
```
GET /metrics
```

Key metrics:
- `ach_files_uploaded_total` - Total files uploaded
- `ach_entries_processed_total` - Entries processed (by status)
- `rtp_messages_published_total` - Messages published (by status)
- `conversion_job_duration_seconds` - Job processing duration
- `active_conversion_jobs` - Currently active jobs

### Logging
All logs are structured JSON format for easy parsing and analysis.

Example log entry:
```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "event_id": "550e8400-e29b-41d4-a716-446655440000",
  "action": "FILE_UPLOAD",
  "resource_type": "ACH_FILE",
  "resource_id": "payroll.ach",
  "result": "SUCCESS",
  "details": {
    "job_id": "550e8400-e29b-41d4-a716-446655440000",
    "file_size": 94000,
    "source_system": "payroll-system"
  }
}
```

## 🔐 Security

- Non-root container user (UID 1000)
- Environment-based configuration (no hardcoded secrets)
- Input validation and XML special character escaping
- Comprehensive error handling without information leakage
- Audit logging for compliance

## 📈 Performance

- Async/await for non-blocking I/O
- Connection pooling for database and message queue
- Batch processing support for multiple entries
- Configurable timeouts and retry policies
- Prometheus metrics for monitoring

## 🐛 Troubleshooting

### Database Connection Issues
```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Verify connection
psql -h localhost -U postgres -d ach_rtp_db -c "SELECT 1"
```

### RabbitMQ Connection Issues
```bash
# Check RabbitMQ is running
docker-compose ps rabbitmq

# Access management console
# http://localhost:15672 (guest/guest)
```

### Application Logs
```bash
# View recent logs
docker-compose logs -f ach-to-rtp-service

# View specific number of lines
docker-compose logs --tail=100 ach-to-rtp-service
```

## 📝 License

Proprietary - All rights reserved

## 👥 Support

For issues, questions, or contributions, please contact the development team.
=======
# autonomipay
autonomipay 
>>>>>>> c288917db5abdced6baf730e953bff2ef20bcfc1
