# API Documentation

## Overview

The ACH to RTP Conversion Service provides REST API endpoints for file upload, conversion status tracking, and health monitoring.

## Base URL

```
http://localhost:8080/api
```

## Authentication

Currently, the service does not implement authentication. In production, add OAuth2 or API key authentication.

## Endpoints

### File Upload and Conversion

#### POST /v1/conversion/upload

Upload an ACH file and convert it to RTP messages.

**Request:**
```bash
curl -X POST \
  -F "file=@sample.ach" \
  http://localhost:8080/api/v1/conversion/upload
```

**Request Parameters:**
- `file` (multipart/form-data, required): ACH file to upload (max 10 MB)

**Response (200 OK):**
```json
{
  "fileName": "sample.ach",
  "status": "COMPLETED",
  "totalEntries": 100,
  "successfulConversions": 98,
  "failedConversions": 2,
  "errorMessage": null,
  "errors": [
    {
      "entryId": "000000000000001",
      "errorMessage": "Invalid routing number format"
    },
    {
      "entryId": "000000000000002",
      "errorMessage": "Missing account number"
    }
  ]
}
```

**Response (400 Bad Request):**
```json
{
  "status": "ERROR",
  "errorType": "FILE_SIZE_EXCEEDED",
  "message": "Uploaded file exceeds maximum allowed size",
  "maxSize": "10 MB",
  "timestamp": 1704067200000
}
```

**Response (500 Internal Server Error):**
```json
{
  "status": "ERROR",
  "errorType": "INTERNAL_SERVER_ERROR",
  "message": "An unexpected error occurred",
  "timestamp": 1704067200000
}
```

**Status Codes:**
- `200 OK`: Conversion completed (check `status` field for result)
- `400 Bad Request`: Invalid file or file too large
- `500 Internal Server Error`: Server error during processing

---

### Conversion Status

#### GET /v1/jobs/{jobId}

Get the status of a conversion job.

**Request:**
```bash
curl http://localhost:8080/api/v1/jobs/abc123def456
```

**Response (200 OK):**
```json
{
  "jobId": "abc123def456",
  "status": "COMPLETED",
  "totalEntries": 100,
  "successfulConversions": 98,
  "failedConversions": 2,
  "timestamp": 1704067200000
}
```

**Status Values:**
- `PROCESSING`: Job is currently being processed
- `COMPLETED`: Job completed (check success/failure counts)
- `FAILED`: Job failed with error

---

#### GET /v1/jobs

List all conversion jobs with optional filtering.

**Request:**
```bash
curl "http://localhost:8080/api/v1/jobs?status=COMPLETED&limit=50"
```

**Query Parameters:**
- `status` (optional): Filter by status (PROCESSING, COMPLETED, FAILED)
- `limit` (optional, default: 50): Maximum number of results

**Response (200 OK):**
```json
{
  "jobs": [
    {
      "jobId": "abc123def456",
      "fileName": "sample.ach",
      "status": "COMPLETED",
      "totalEntries": 100,
      "successfulConversions": 98,
      "failedConversions": 2,
      "timestamp": 1704067200000
    }
  ],
  "total": 1,
  "limit": 50,
  "timestamp": 1704067200000
}
```

---

#### GET /v1/jobs/{jobId}/errors

Get detailed error information for a failed job.

**Request:**
```bash
curl http://localhost:8080/api/v1/jobs/abc123def456/errors
```

**Response (200 OK):**
```json
{
  "jobId": "abc123def456",
  "errors": [
    {
      "entryId": "000000000000001",
      "errorMessage": "Invalid routing number format"
    },
    {
      "entryId": "000000000000002",
      "errorMessage": "Missing account number"
    }
  ],
  "errorCount": 2,
  "timestamp": 1704067200000
}
```

---

#### POST /v1/jobs/{jobId}/retry

Retry a failed conversion job.

**Request:**
```bash
curl -X POST http://localhost:8080/api/v1/jobs/abc123def456/retry
```

**Response (202 Accepted):**
```json
{
  "jobId": "abc123def456",
  "status": "RETRYING",
  "message": "Job retry initiated",
  "timestamp": 1704067200000
}
```

---

### Health Checks

#### GET /v1/health/status

Get service health status.

**Request:**
```bash
curl http://localhost:8080/api/v1/health/status
```

**Response (200 OK):**
```json
{
  "status": "UP",
  "service": "ach-to-rtp-service",
  "version": "1.0.0",
  "timestamp": 1704067200000
}
```

---

#### GET /v1/health/live

Kubernetes liveness probe endpoint.

**Request:**
```bash
curl http://localhost:8080/api/v1/health/live
```

**Response (200 OK):**
```json
{
  "status": "UP"
}
```

---

#### GET /v1/health/ready

Kubernetes readiness probe endpoint.

**Request:**
```bash
curl http://localhost:8080/api/v1/health/ready
```

**Response (200 OK):**
```json
{
  "status": "READY"
}
```

---

## Error Responses

All error responses follow a consistent format:

```json
{
  "status": "ERROR",
  "errorType": "ERROR_TYPE",
  "message": "Human-readable error message",
  "timestamp": 1704067200000
}
```

### Error Types

| Error Type | HTTP Status | Description |
|-----------|------------|-------------|
| `ACH_PARSING_ERROR` | 400 | Failed to parse ACH file |
| `RTP_MESSAGE_ERROR` | 500 | Failed to generate RTP message |
| `PUBLISHING_ERROR` | 503 | Failed to publish message to queue |
| `VALIDATION_ERROR` | 400 | Validation of data failed |
| `FILE_SIZE_EXCEEDED` | 413 | Uploaded file exceeds maximum size |
| `INTERNAL_SERVER_ERROR` | 500 | Unexpected server error |

---

## Request/Response Examples

### Example 1: Successful File Upload

**Request:**
```bash
curl -X POST \
  -F "file=@ach_file_20240101.ach" \
  http://localhost:8080/api/v1/conversion/upload
```

**Response:**
```json
{
  "fileName": "ach_file_20240101.ach",
  "status": "COMPLETED",
  "totalEntries": 500,
  "successfulConversions": 500,
  "failedConversions": 0,
  "errorMessage": null,
  "errors": []
}
```

### Example 2: Partial Failure

**Request:**
```bash
curl -X POST \
  -F "file=@ach_file_20240102.ach" \
  http://localhost:8080/api/v1/conversion/upload
```

**Response:**
```json
{
  "fileName": "ach_file_20240102.ach",
  "status": "COMPLETED",
  "totalEntries": 100,
  "successfulConversions": 98,
  "failedConversions": 2,
  "errorMessage": null,
  "errors": [
    {
      "entryId": "000000000000050",
      "errorMessage": "Invalid routing number: 00000000"
    },
    {
      "entryId": "000000000000075",
      "errorMessage": "Missing receiving account number"
    }
  ]
}
```

### Example 3: File Too Large

**Request:**
```bash
curl -X POST \
  -F "file=@large_file.ach" \
  http://localhost:8080/api/v1/conversion/upload
```

**Response (413 Payload Too Large):**
```json
{
  "status": "ERROR",
  "errorType": "FILE_SIZE_EXCEEDED",
  "message": "Uploaded file exceeds maximum allowed size",
  "maxSize": "10 MB",
  "timestamp": 1704067200000
}
```

---

## Rate Limiting

Currently, the service does not implement rate limiting. In production, add rate limiting to prevent abuse:

- Recommended: 100 requests per minute per IP
- File upload: 10 files per minute per IP

---

## Pagination

List endpoints support pagination:

```bash
curl "http://localhost:8080/api/v1/jobs?limit=25&offset=0"
```

**Query Parameters:**
- `limit`: Maximum number of results (default: 50, max: 100)
- `offset`: Number of results to skip (default: 0)

---

## Filtering

List endpoints support filtering:

```bash
curl "http://localhost:8080/api/v1/jobs?status=COMPLETED&fileName=sample.ach"
```

**Supported Filters:**
- `status`: PROCESSING, COMPLETED, FAILED
- `fileName`: Partial filename match
- `createdAfter`: ISO 8601 date (e.g., 2024-01-01T00:00:00Z)
- `createdBefore`: ISO 8601 date

---

## Versioning

The API uses URL versioning (e.g., `/v1/`). Future versions will be available as `/v2/`, etc.

---

## Deprecation

Deprecated endpoints will be marked with a `Deprecation` header:

```
Deprecation: true
Sunset: Sun, 31 Dec 2024 23:59:59 GMT
```

---

## Support

For API issues or questions, contact the development team.
