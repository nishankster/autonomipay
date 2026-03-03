# MFA Microservice Deployment Guide

This guide covers deploying the MFA microservice to various environments.

## Local Development

### Prerequisites

- Python 3.11+
- PostgreSQL 14+
- Docker and Docker Compose (optional)

### Quick Start with Docker Compose

The easiest way to get started is using Docker Compose:

```bash
cd server/mfa_service
docker-compose up -d
```

This will:
1. Start a PostgreSQL database on port 5432
2. Initialize the database schema
3. Start the MFA API on port 8000

Access the Swagger documentation at: `http://localhost:8000/docs`

### Manual Setup

1. **Create PostgreSQL database:**

```bash
psql -U postgres
CREATE USER mfa_user WITH PASSWORD 'mfa_password';
CREATE DATABASE mfa_db OWNER mfa_user;
GRANT ALL PRIVILEGES ON DATABASE mfa_db TO mfa_user;
```

2. **Set up Python environment:**

```bash
cd server/mfa_service
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. **Configure environment variables:**

```bash
cp .env.example .env
# Edit .env with your configuration
```

4. **Initialize database:**

```bash
python -c "from database import init_db; init_db()"
```

5. **Run the service:**

```bash
python main.py
```

The API will be available at `http://localhost:8000`

## Production Deployment

### Docker Build

Build the Docker image:

```bash
cd server/mfa_service
docker build -t mfa-microservice:1.0.0 .
```

Run the container:

```bash
docker run -d \
  --name mfa_api \
  -p 8000:8000 \
  -e DATABASE_URL=postgresql://mfa_user:password@db_host:5432/mfa_db \
  -e JWT_SECRET_KEY=your-production-secret-key \
  -e ORIGIN=https://your-domain.com \
  -e RP_ID=your-domain.com \
  mfa-microservice:1.0.0
```

### Kubernetes Deployment

Create a Kubernetes deployment manifest (`k8s/deployment.yaml`):

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mfa-microservice
  labels:
    app: mfa-microservice
spec:
  replicas: 3
  selector:
    matchLabels:
      app: mfa-microservice
  template:
    metadata:
      labels:
        app: mfa-microservice
    spec:
      containers:
      - name: mfa-api
        image: mfa-microservice:1.0.0
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: mfa-secrets
              key: database-url
        - name: JWT_SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: mfa-secrets
              key: jwt-secret
        - name: ORIGIN
          value: "https://your-domain.com"
        - name: RP_ID
          value: "your-domain.com"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 10
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
---
apiVersion: v1
kind: Service
metadata:
  name: mfa-microservice
spec:
  selector:
    app: mfa-microservice
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer
```

Deploy to Kubernetes:

```bash
kubectl create secret generic mfa-secrets \
  --from-literal=database-url=postgresql://... \
  --from-literal=jwt-secret=your-secret-key

kubectl apply -f k8s/deployment.yaml
```

### AWS ECS Deployment

Create an ECS task definition:

```json
{
  "family": "mfa-microservice",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "256",
  "memory": "512",
  "containerDefinitions": [
    {
      "name": "mfa-api",
      "image": "your-ecr-registry/mfa-microservice:1.0.0",
      "portMappings": [
        {
          "containerPort": 8000,
          "hostPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "ORIGIN",
          "value": "https://your-domain.com"
        },
        {
          "name": "RP_ID",
          "value": "your-domain.com"
        }
      ],
      "secrets": [
        {
          "name": "DATABASE_URL",
          "valueFrom": "arn:aws:secretsmanager:region:account:secret:mfa/database-url"
        },
        {
          "name": "JWT_SECRET_KEY",
          "valueFrom": "arn:aws:secretsmanager:region:account:secret:mfa/jwt-secret"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/mfa-microservice",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

### Google Cloud Run Deployment

1. **Build and push to Container Registry:**

```bash
gcloud builds submit --tag gcr.io/PROJECT_ID/mfa-microservice:1.0.0
```

2. **Deploy to Cloud Run:**

```bash
gcloud run deploy mfa-microservice \
  --image gcr.io/PROJECT_ID/mfa-microservice:1.0.0 \
  --platform managed \
  --region us-central1 \
  --set-env-vars DATABASE_URL=postgresql://...,JWT_SECRET_KEY=...,ORIGIN=https://...,RP_ID=...
```

### Azure Container Instances

1. **Push to Azure Container Registry:**

```bash
az acr build --registry myregistry --image mfa-microservice:1.0.0 .
```

2. **Deploy to Container Instances:**

```bash
az container create \
  --resource-group myresourcegroup \
  --name mfa-microservice \
  --image myregistry.azurecr.io/mfa-microservice:1.0.0 \
  --cpu 1 \
  --memory 1 \
  --port 8000 \
  --environment-variables \
    DATABASE_URL=postgresql://... \
    JWT_SECRET_KEY=... \
    ORIGIN=https://your-domain.com \
    RP_ID=your-domain.com
```

## Environment Configuration

### Required Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@host:5432/db` |
| `JWT_SECRET_KEY` | Secret key for JWT signing | `your-super-secret-key` |
| `ORIGIN` | CORS origin for FIDO2 verification | `https://your-domain.com` |
| `RP_ID` | Relying Party ID for FIDO2 | `your-domain.com` |

### Optional Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `RP_NAME` | MFA Service | Relying Party name |
| `JWT_ALGORITHM` | HS256 | JWT signing algorithm |
| `JWT_EXPIRATION_HOURS` | 24 | Token expiration in hours |
| `BCRYPT_ROUNDS` | 12 | Bcrypt hashing rounds |
| `DEBUG` | False | Enable debug mode |
| `CORS_ORIGINS` | localhost | Allowed CORS origins |

## Database Setup

### PostgreSQL Configuration

For production, enable SSL and configure backups:

```sql
-- Enable SSL
ALTER SYSTEM SET ssl = on;
SELECT pg_reload_conf();

-- Create backup user
CREATE USER backup_user WITH PASSWORD 'backup_password';
GRANT CONNECT ON DATABASE mfa_db TO backup_user;
GRANT USAGE ON SCHEMA public TO backup_user;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO backup_user;
```

### Backup Strategy

Daily automated backups:

```bash
#!/bin/bash
# backup.sh
BACKUP_DIR="/backups/mfa"
DATE=$(date +%Y%m%d_%H%M%S)

pg_dump -h localhost -U mfa_user -d mfa_db | gzip > $BACKUP_DIR/mfa_db_$DATE.sql.gz

# Keep only last 30 days
find $BACKUP_DIR -name "mfa_db_*.sql.gz" -mtime +30 -delete
```

Schedule with cron:

```bash
0 2 * * * /path/to/backup.sh
```

## Monitoring & Logging

### Health Checks

The service exposes a health check endpoint:

```bash
curl http://localhost:8000/health
```

Configure monitoring:

```bash
# Prometheus scrape config
scrape_configs:
  - job_name: 'mfa-microservice'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
```

### Logging

Logs are written to stdout. Configure log aggregation:

```bash
# Docker logging driver
docker run -d \
  --log-driver=awslogs \
  --log-opt awslogs-group=/ecs/mfa \
  --log-opt awslogs-region=us-east-1 \
  mfa-microservice:1.0.0
```

## Security Checklist

- [ ] Change `JWT_SECRET_KEY` to a strong random value
- [ ] Configure `ORIGIN` and `RP_ID` for your domain
- [ ] Enable HTTPS/TLS for all endpoints
- [ ] Configure firewall rules to restrict database access
- [ ] Enable database encryption at rest
- [ ] Set up regular backups
- [ ] Configure monitoring and alerting
- [ ] Enable audit logging
- [ ] Rotate credentials regularly
- [ ] Keep dependencies updated

## Troubleshooting

### Database Connection Error

```
ERROR: could not translate host name "postgres" to address
```

Ensure PostgreSQL is running and the DATABASE_URL is correct.

### FIDO2 Verification Fails

Ensure `ORIGIN` and `RP_ID` match your deployment domain exactly.

### JWT Token Invalid

Ensure all instances share the same `JWT_SECRET_KEY`.

## Performance Tuning

### PostgreSQL Optimization

```sql
-- Increase shared buffers (25% of RAM)
ALTER SYSTEM SET shared_buffers = '4GB';

-- Increase effective cache size (50-75% of RAM)
ALTER SYSTEM SET effective_cache_size = '12GB';

-- Increase work memory
ALTER SYSTEM SET work_mem = '10MB';

-- Enable parallel queries
ALTER SYSTEM SET max_parallel_workers_per_gather = 4;
```

### Application Optimization

- Use connection pooling (PgBouncer)
- Enable caching for frequently accessed data
- Monitor slow queries
- Optimize database indexes

## Scaling

### Horizontal Scaling

Deploy multiple instances behind a load balancer:

```nginx
upstream mfa_backend {
    server mfa1.example.com:8000;
    server mfa2.example.com:8000;
    server mfa3.example.com:8000;
}

server {
    listen 443 ssl;
    server_name api.example.com;

    location / {
        proxy_pass http://mfa_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Database Scaling

For high traffic, consider:
- Read replicas for queries
- Connection pooling (PgBouncer)
- Partitioning large tables
- Archiving old audit logs

## Support

For issues and questions, please open an issue on the project repository or contact support@manus.im.

---

**Version**: 1.0.0  
**Last Updated**: February 27, 2026
