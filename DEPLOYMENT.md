# ACH to RTP Conversion Service - Deployment Guide

This guide covers deploying the ACH to RTP Conversion Service to various environments including local development, Docker, Kubernetes, and production cloud platforms.

## Table of Contents

1. [Local Development](#local-development)
2. [Docker Deployment](#docker-deployment)
3. [Kubernetes Deployment](#kubernetes-deployment)
4. [Production Deployment](#production-deployment)
5. [Environment Configuration](#environment-configuration)
6. [Monitoring and Observability](#monitoring-and-observability)
7. [Troubleshooting](#troubleshooting)

---

## Local Development

### Prerequisites

| Component | Version | Purpose |
|-----------|---------|---------|
| **Python** | 3.11+ | Runtime |
| **PostgreSQL** | 13+ | Database |
| **RabbitMQ** | 3.10+ | Message broker |
| **Docker** | 20.10+ | Container runtime (optional) |
| **Docker Compose** | 2.0+ | Multi-container orchestration |

### Quick Setup

**Step 1: Clone and setup environment**

```bash
cd /home/ubuntu/ach-to-rtp-service
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**Step 2: Start dependencies with Docker Compose**

```bash
docker-compose up -d
```

This starts PostgreSQL and RabbitMQ automatically configured for local development.

**Step 3: Run the application**

```bash
python -m uvicorn app.main:app --reload
```

The service will start on `http://localhost:8000`

**Step 4: Verify the service**

```bash
curl http://localhost:8000/api/v1/health/status
```

### Manual Database and RabbitMQ Setup

If you prefer to run PostgreSQL and RabbitMQ manually:

**Start PostgreSQL**:

```bash
docker run -d \
  --name postgres \
  -e POSTGRES_DB=ach_rtp_db \
  -e POSTGRES_PASSWORD=postgres \
  -p 5432:5432 \
  postgres:15-alpine
```

**Start RabbitMQ**:

```bash
docker run -d \
  --name rabbitmq \
  -p 5672:5672 \
  -p 15672:15672 \
  rabbitmq:3.12-management-alpine
```

**Create database**:

```bash
psql -h localhost -U postgres -d ach_rtp_db -c "SELECT 1"
```

---

## Docker Deployment

### Build Docker Image

```bash
# Build the image
docker build -t ach-to-rtp-service:1.0.0 .

# Tag for registry
docker tag ach-to-rtp-service:1.0.0 myregistry.azurecr.io/ach-to-rtp-service:1.0.0

# Push to registry
docker push myregistry.azurecr.io/ach-to-rtp-service:1.0.0
```

### Run with Docker Compose

**Start all services**:

```bash
docker-compose up -d
```

**View logs**:

```bash
docker-compose logs -f ach-to-rtp-service
```

**Stop services**:

```bash
docker-compose down
```

### Run Standalone Container

```bash
docker run -d \
  -p 8080:8000 \
  -e DATABASE_URL=postgresql+asyncpg://postgres:postgres@postgres:5432/ach_rtp_db \
  -e RABBITMQ_HOST=rabbitmq \
  -e RABBITMQ_PORT=5672 \
  --name ach-rtp-service \
  ach-to-rtp-service:1.0.0
```

### Docker Image Optimization

The Dockerfile uses multi-stage builds to minimize image size:

- **Builder stage**: Installs dependencies and compiles packages
- **Runtime stage**: Contains only runtime dependencies and application code

This reduces the final image size from ~1.2GB to ~500MB.

---

## Kubernetes Deployment

### Prerequisites

- Kubernetes cluster (1.24+)
- kubectl configured
- Helm (optional, for package management)
- PostgreSQL and RabbitMQ services available

### Quick Deployment

**Step 1: Create namespace**

```bash
kubectl create namespace ach-rtp
```

**Step 2: Create secrets**

```bash
kubectl create secret generic ach-rtp-secrets \
  --from-literal=database-url=postgresql+asyncpg://postgres:postgres@postgres:5432/ach_rtp_db \
  --from-literal=rabbitmq-host=rabbitmq \
  --from-literal=rabbitmq-port=5672 \
  -n ach-rtp
```

**Step 3: Apply manifests**

```bash
kubectl apply -f k8s/ -n ach-rtp
```

**Step 4: Verify deployment**

```bash
kubectl get pods -n ach-rtp
kubectl logs -f deployment/ach-to-rtp-service -n ach-rtp
```

### Kubernetes Manifests

The `k8s/` directory contains the following manifests:

| File | Purpose |
|------|---------|
| `deployment.yaml` | Pod deployment with replicas |
| `service.yaml` | Service for internal/external access |
| `configmap.yaml` | Configuration data |
| `secret.yaml` | Secrets template (update with actual values) |
| `rbac.yaml` | ServiceAccount and RBAC policies |
| `hpa.yaml` | Horizontal Pod Autoscaler |
| `pdb.yaml` | Pod Disruption Budget |

### Scaling

**Manual scaling**:

```bash
kubectl scale deployment/ach-to-rtp-service --replicas=3 -n ach-rtp
```

**Auto-scaling** (already configured in HPA):

```bash
kubectl get hpa -n ach-rtp
```

The HPA automatically scales pods based on CPU and memory usage.

### Rolling Updates

```bash
# Update image
kubectl set image deployment/ach-to-rtp-service \
  ach-to-rtp-service=myregistry.azurecr.io/ach-to-rtp-service:2.0.0 \
  -n ach-rtp

# Monitor rollout
kubectl rollout status deployment/ach-to-rtp-service -n ach-rtp

# Rollback if needed
kubectl rollout undo deployment/ach-to-rtp-service -n ach-rtp
```

### Port Forwarding

```bash
kubectl port-forward svc/ach-to-rtp-service 8080:8000 -n ach-rtp
```

Then access the service at `http://localhost:8080`

---

## Production Deployment

### Pre-Deployment Checklist

- [ ] All tests passing (`pytest tests/`)
- [ ] Code reviewed and merged to main branch
- [ ] Docker image built and pushed to registry
- [ ] Environment variables configured
- [ ] Database backups configured
- [ ] Monitoring and alerting configured
- [ ] Load testing completed
- [ ] Security scanning completed

### Cloud Platform Deployment

#### AWS ECS

```bash
# Create ECR repository
aws ecr create-repository --repository-name ach-to-rtp-service

# Build and push image
docker build -t ach-to-rtp-service:1.0.0 .
docker tag ach-to-rtp-service:1.0.0 <account-id>.dkr.ecr.<region>.amazonaws.com/ach-to-rtp-service:1.0.0
docker push <account-id>.dkr.ecr.<region>.amazonaws.com/ach-to-rtp-service:1.0.0

# Create ECS task definition and service
# (See AWS documentation for detailed steps)
```

#### Azure Container Instances

```bash
# Create container registry
az acr create --resource-group myResourceGroup --name myRegistry --sku Basic

# Build and push image
az acr build --registry myRegistry --image ach-to-rtp-service:1.0.0 .

# Deploy container instance
az container create \
  --resource-group myResourceGroup \
  --name ach-to-rtp-service \
  --image myRegistry.azurecr.io/ach-to-rtp-service:1.0.0 \
  --ports 8000 \
  --environment-variables \
    DATABASE_URL=postgresql+asyncpg://... \
    RABBITMQ_HOST=...
```

#### Google Cloud Run

```bash
# Build and push image
gcloud builds submit --tag gcr.io/PROJECT_ID/ach-to-rtp-service:1.0.0

# Deploy to Cloud Run
gcloud run deploy ach-to-rtp-service \
  --image gcr.io/PROJECT_ID/ach-to-rtp-service:1.0.0 \
  --platform managed \
  --region us-central1 \
  --set-env-vars DATABASE_URL=...,RABBITMQ_HOST=...
```

### Production Configuration

**Environment Variables**:

```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/ach_rtp_db
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=40

# RabbitMQ
RABBITMQ_HOST=rabbitmq.example.com
RABBITMQ_PORT=5672
RABBITMQ_USER=ach_user
RABBITMQ_PASSWORD=secure_password
RABBITMQ_VHOST=/ach-rtp

# Application
APP_NAME=ACH to RTP Conversion Service
APP_VERSION=1.0.0
LOG_LEVEL=INFO
ENVIRONMENT=production

# File Upload
MAX_FILE_SIZE_MB=100
ALLOWED_FILE_EXTENSIONS=.ach

# Processing
BATCH_SIZE=100
TIMEOUT_SECONDS=300
MAX_RETRIES=3
```

### SSL/TLS Configuration

For production, enable SSL/TLS with a reverse proxy (nginx, Traefik, etc.):

```nginx
server {
    listen 443 ssl http2;
    server_name ach-rtp.example.com;

    ssl_certificate /etc/ssl/certs/server.crt;
    ssl_certificate_key /etc/ssl/private/server.key;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## Environment Configuration

### Configuration Files

- `.env` - Local development (not committed)
- `.env.example` - Template for environment variables
- `app/config/settings.py` - Python settings module

### Environment Profiles

The application supports different profiles:

```bash
# Development (default)
python -m uvicorn app.main:app --reload

# Production
ENVIRONMENT=production python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Secrets Management

**Option 1: Environment Variables**

```bash
export DATABASE_URL=postgresql+asyncpg://...
export RABBITMQ_HOST=rabbitmq.example.com
python -m uvicorn app.main:app
```

**Option 2: .env File**

```bash
# Create .env file
cp .env.example .env
# Edit .env with actual values
python -m uvicorn app.main:app
```

**Option 3: Kubernetes Secrets**

```bash
kubectl create secret generic ach-rtp-secrets \
  --from-literal=database-url=postgresql+asyncpg://... \
  --from-literal=rabbitmq-host=... \
  -n ach-rtp
```

---

## Monitoring and Observability

### Prometheus Metrics

The service exposes Prometheus metrics at `/metrics`:

```bash
curl http://localhost:8000/metrics
```

**Configure Prometheus**:

```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'ach-to-rtp-service'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
```

### Structured Logging

Logs are output as JSON for easy parsing and aggregation:

```bash
# View logs
docker-compose logs -f ach-to-rtp-service | jq .

# Send to log aggregation service
# Configure in docker-compose.yml or Kubernetes
```

### Health Checks

**Liveness probe** (Kubernetes):

```yaml
livenessProbe:
  httpGet:
    path: /api/v1/health/live
    port: 8000
  initialDelaySeconds: 10
  periodSeconds: 10
```

**Readiness probe** (Kubernetes):

```yaml
readinessProbe:
  httpGet:
    path: /api/v1/health/ready
    port: 8000
  initialDelaySeconds: 5
  periodSeconds: 5
```

### Alerting

Configure alerts for:

- Service down (liveness probe failure)
- High error rate (> 5%)
- High latency (> 5 seconds)
- Database connection failures
- RabbitMQ connection failures

---

## Troubleshooting

### Service Won't Start

**Check logs**:

```bash
docker-compose logs ach-to-rtp-service
# or
kubectl logs deployment/ach-to-rtp-service -n ach-rtp
```

**Common issues**:

- Database connection error: Verify DATABASE_URL and PostgreSQL is running
- RabbitMQ connection error: Verify RABBITMQ_HOST and RabbitMQ is running
- Port already in use: Change port or stop other services

### Database Connection Issues

```bash
# Test connection
psql -h localhost -U postgres -d ach_rtp_db

# Check connection pool
# Monitor in app logs for "connection pool exhausted"
```

### RabbitMQ Connection Issues

```bash
# Check RabbitMQ status
docker exec rabbitmq rabbitmqctl status

# View RabbitMQ management UI
# http://localhost:15672 (guest/guest)
```

### High Memory Usage

- Reduce `DATABASE_POOL_SIZE` in environment variables
- Increase container memory limits
- Monitor for memory leaks in application logs

### Slow Processing

- Check database query performance
- Monitor RabbitMQ queue depth
- Increase number of replicas for horizontal scaling
- Optimize batch size

### File Upload Failures

- Check `MAX_FILE_SIZE_MB` setting
- Verify file is UTF-8 encoded
- Check available disk space
- Monitor network bandwidth

---

## Backup and Recovery

### Database Backups

```bash
# Backup PostgreSQL
pg_dump -h localhost -U postgres ach_rtp_db > backup.sql

# Restore from backup
psql -h localhost -U postgres ach_rtp_db < backup.sql
```

### Disaster Recovery

1. **Backup strategy**: Daily backups to cloud storage
2. **Recovery time objective (RTO)**: 1 hour
3. **Recovery point objective (RPO)**: 1 hour
4. **Test recovery**: Monthly recovery drills

---

## Performance Tuning

### Database Optimization

```sql
-- Create indexes for common queries
CREATE INDEX idx_job_status ON jobs(status);
CREATE INDEX idx_job_created_at ON jobs(created_at);
CREATE INDEX idx_error_job_id ON errors(job_id);
```

### Connection Pooling

```python
# In app/config/database.py
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_size=20,
    max_overflow=40,
    pool_pre_ping=True,
)
```

### Caching

Consider implementing caching for:

- Job status queries
- Health check results
- Configuration values

---

## Security Hardening

- [ ] Enable HTTPS/TLS
- [ ] Implement rate limiting
- [ ] Add API authentication (OAuth2, API keys)
- [ ] Enable CORS only for trusted origins
- [ ] Regularly update dependencies
- [ ] Scan for vulnerabilities
- [ ] Implement request validation
- [ ] Log security events

---

## Maintenance

### Regular Tasks

- Monitor logs for errors
- Review metrics and performance
- Update dependencies monthly
- Rotate secrets quarterly
- Test disaster recovery annually

### Upgrade Procedure

1. Test upgrade in staging environment
2. Create database backup
3. Deploy new version with rolling update
4. Monitor for errors
5. Rollback if issues detected

---

## Support

For deployment issues or questions, refer to the troubleshooting section or contact the development team.
