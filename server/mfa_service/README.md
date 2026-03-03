# MFA Microservice API

A production-grade Multi-Factor Authentication microservice built with FastAPI, supporting FIDO2/WebAuthn, device binding, and biometric authentication.

## Features

- **FIDO2/WebAuthn Support**: Passwordless authentication using security keys and biometric authenticators
- **Device Management**: Register, trust, and manage user devices
- **Device Binding**: Cryptographic binding of credentials to specific devices
- **Biometric Authentication**: Support for fingerprint, face recognition, and other biometric methods
- **Audit Logging**: Comprehensive security event logging
- **JWT Token Management**: Secure token generation and validation
- **PostgreSQL Backend**: Encrypted data storage with proper indexing

## Project Structure

```
server/mfa_service/
├── main.py                 # FastAPI application and endpoints
├── models.py              # SQLAlchemy ORM models
├── schemas.py             # Pydantic request/response schemas
├── services.py            # Business logic services
├── security.py            # Encryption, hashing, JWT utilities
├── config.py              # Configuration management
├── database.py            # Database connection and session management
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## Setup & Installation

### Prerequisites

- Python 3.11+
- PostgreSQL 14+
- pip/venv

### 1. Create Virtual Environment

```bash
cd server/mfa_service
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Database

Create a PostgreSQL database and user:

```sql
CREATE USER mfa_user WITH PASSWORD 'mfa_password';
CREATE DATABASE mfa_db OWNER mfa_user;
GRANT ALL PRIVILEGES ON DATABASE mfa_db TO mfa_user;
```

### 4. Set Environment Variables

Create a `.env` file in the `server/mfa_service` directory:

```bash
DATABASE_URL=postgresql://mfa_user:mfa_password@localhost:5432/mfa_db
JWT_SECRET_KEY=your-super-secret-key-change-in-production
ORIGIN=http://localhost:8000
RP_ID=localhost
RP_NAME=MFA Service
```

### 5. Initialize Database

```bash
python -c "from database import init_db; init_db()"
```

## Running the Service

### Development Mode

```bash
source venv/bin/activate
python main.py
```

The API will be available at `http://localhost:8000`

### Production Mode

```bash
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API Endpoints

### Health Check

```
GET /health
```

### User Registration

```
POST /auth/register
Content-Type: application/json

{
  "username": "john_doe",
  "email": "john@example.com",
  "device_name": "iPhone 15 Pro"
}
```

### FIDO2 Registration

**Begin Registration:**
```
POST /auth/fido2/register/begin
Content-Type: application/json

{
  "user_id": "uuid"
}
```

**Complete Registration:**
```
POST /auth/fido2/register/complete
Content-Type: application/json

{
  "user_id": "uuid",
  "attestation_object": "base64_encoded",
  "client_data_json": "base64_encoded",
  "device_id": "uuid"
}
```

### FIDO2 Authentication

**Begin Authentication:**
```
POST /auth/fido2/authenticate/begin
Content-Type: application/json

{
  "username": "john_doe"
}
```

**Complete Authentication:**
```
POST /auth/fido2/authenticate/complete
Content-Type: application/json

{
  "username": "john_doe",
  "assertion_object": "base64_encoded",
  "client_data_json": "base64_encoded",
  "device_id": "uuid"
}
```

### Device Management

**Register Device:**
```
POST /devices/register?user_id=uuid
Content-Type: application/json

{
  "device_name": "iPhone 15 Pro",
  "device_type": "iOS",
  "device_os": "17.2.1",
  "device_model": "iPhone15,3",
  "device_fingerprint": "hash"
}
```

**List Devices:**
```
GET /devices?user_id=uuid
```

**Trust Device:**
```
PUT /devices/{device_id}/trust
Content-Type: application/json

{
  "is_trusted": true
}
```

**Revoke Device:**
```
DELETE /devices/{device_id}
```

### Biometric Authentication

**Register Biometric:**
```
POST /biometric/register?user_id=uuid
Content-Type: application/json

{
  "device_id": "uuid",
  "method_type": "fingerprint",
  "biometric_data": "encrypted_template"
}
```

**Verify Biometric:**
```
POST /biometric/verify?user_id=uuid
Content-Type: application/json

{
  "device_id": "uuid",
  "method_type": "fingerprint",
  "biometric_input": "encrypted_template"
}
```

## Testing

Run unit tests:

```bash
pytest tests/ -v
```

Run with coverage:

```bash
pytest tests/ --cov=. --cov-report=html
```

## Security Considerations

- All sensitive data is encrypted at rest using AES-256-GCM
- Passwords are hashed using bcrypt with 12 rounds
- JWT tokens are signed with HS256
- All API endpoints use HTTPS in production
- Device fingerprints are hashed with PBKDF2
- FIDO2 signatures are verified using public key cryptography
- Audit logs track all security events

## Database Schema

The microservice uses the following main tables:

- **users**: User accounts and authentication
- **devices**: Registered devices with trust status
- **fido2_credentials**: FIDO2 public key credentials
- **biometric_methods**: Registered biometric authentication methods
- **mfa_sessions**: Active MFA challenges and sessions
- **audit_logs**: Security event audit trail

## Performance Optimization

- Database queries are indexed for fast lookups
- Connection pooling is configured for PostgreSQL
- JWT tokens are cached to reduce verification overhead
- Credential lookups use indexed credential IDs

## Deployment

### Docker

Create a `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:

```bash
docker build -t mfa-service .
docker run -p 8000:8000 -e DATABASE_URL=postgresql://... mfa-service
```

### Kubernetes

Deploy using Kubernetes manifests (see `k8s/` directory for examples).

## Monitoring

The service exposes metrics at `/metrics` for Prometheus scraping.

Key metrics:
- `auth_success_rate`: Authentication success rate
- `api_response_time`: API endpoint response times
- `device_registration_count`: Total registered devices
- `failed_auth_attempts`: Failed authentication attempts

## Troubleshooting

### Database Connection Error

Ensure PostgreSQL is running and the connection string is correct:

```bash
psql postgresql://mfa_user:mfa_password@localhost:5432/mfa_db
```

### FIDO2 Verification Fails

Check that the `ORIGIN` and `RP_ID` environment variables match your deployment domain.

### Token Validation Error

Ensure the `JWT_SECRET_KEY` is consistent across all instances.

## Contributing

1. Create a feature branch
2. Make your changes
3. Write tests
4. Submit a pull request

## License

MIT License - See LICENSE file for details

## Support

For issues and questions, please open an issue on the project repository.

---

**Version**: 1.0.0  
**Last Updated**: February 27, 2026  
**Maintainer**: Manus AI
