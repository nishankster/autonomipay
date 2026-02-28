# Deployment Guide

This guide covers deploying the ACH to RTP Conversion Service to various environments.

## Table of Contents

1. [Local Development](#local-development)
2. [Docker Deployment](#docker-deployment)
3. [Kubernetes Deployment](#kubernetes-deployment)
4. [Production Deployment](#production-deployment)
5. [Monitoring and Observability](#monitoring-and-observability)
6. [Troubleshooting](#troubleshooting)

## Local Development

### Prerequisites

- Java 17+
- Maven 3.9+
- PostgreSQL 15+
- RabbitMQ 3.12+

### Setup Steps

1. **Start PostgreSQL**
   ```bash
   # Using Docker
   docker run -d \
     --name postgres \
     -e POSTGRES_DB=ach_rtp_db \
     -e POSTGRES_PASSWORD=postgres \
     -p 5432:5432 \
     postgres:15-alpine
   ```

2. **Start RabbitMQ**
   ```bash
   # Using Docker
   docker run -d \
     --name rabbitmq \
     -p 5672:5672 \
     -p 15672:15672 \
     rabbitmq:3.12-management-alpine
   ```

3. **Build the project**
   ```bash
   mvn clean package
   ```

4. **Run the application**
   ```bash
   mvn spring-boot:run
   ```

5. **Verify the service**
   ```bash
   curl http://localhost:8080/api/v1/health/status
   ```

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

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f ach-to-rtp-service

# Stop all services
docker-compose down
```

### Manual Docker Run

```bash
docker run -d \
  --name ach-to-rtp-service \
  -e SPRING_DATASOURCE_URL=jdbc:postgresql://postgres:5432/ach_rtp_db \
  -e SPRING_DATASOURCE_USERNAME=postgres \
  -e SPRING_DATASOURCE_PASSWORD=postgres \
  -e SPRING_RABBITMQ_HOST=rabbitmq \
  -e SPRING_RABBITMQ_PORT=5672 \
  -p 8080:8080 \
  ach-to-rtp-service:1.0.0
```

## Kubernetes Deployment

### Prerequisites

- Kubernetes cluster (1.24+)
- kubectl configured
- Docker image in accessible registry
- PostgreSQL and RabbitMQ services available

### Deployment Steps

1. **Create namespace** (optional)
   ```bash
   kubectl create namespace ach-rtp
   ```

2. **Update secrets and configmaps**
   ```bash
   # Edit k8s/secret.yaml with production credentials
   # Edit k8s/configmap.yaml with production settings
   ```

3. **Apply manifests**
   ```bash
   # Apply in order
   kubectl apply -f k8s/configmap.yaml
   kubectl apply -f k8s/secret.yaml
   kubectl apply -f k8s/deployment.yaml
   kubectl apply -f k8s/service.yaml
   ```

4. **Verify deployment**
   ```bash
   # Check pods
   kubectl get pods -l app=ach-to-rtp-service

   # Check service
   kubectl get svc ach-to-rtp-service

   # View logs
   kubectl logs -f deployment/ach-to-rtp-service
   ```

5. **Port forward for testing**
   ```bash
   kubectl port-forward svc/ach-to-rtp-service 8080:80
   ```

### Scaling

```bash
# Scale to 5 replicas
kubectl scale deployment ach-to-rtp-service --replicas=5

# Auto-scaling (requires metrics-server)
kubectl autoscale deployment ach-to-rtp-service \
  --min=3 --max=10 --cpu-percent=70
```

### Rolling Update

```bash
# Update image
kubectl set image deployment/ach-to-rtp-service \
  ach-to-rtp-service=myregistry.azurecr.io/ach-to-rtp-service:1.1.0 \
  --record

# Check rollout status
kubectl rollout status deployment/ach-to-rtp-service

# Rollback if needed
kubectl rollout undo deployment/ach-to-rtp-service
```

## Production Deployment

### Pre-Deployment Checklist

- [ ] Database credentials updated in secrets
- [ ] RabbitMQ credentials updated in secrets
- [ ] TLS/SSL certificates configured
- [ ] Log aggregation configured (ELK, Splunk, etc.)
- [ ] Monitoring and alerting set up (Prometheus, Grafana)
- [ ] Backup strategy for database configured
- [ ] Disaster recovery procedures tested
- [ ] Security policies reviewed and approved
- [ ] Load testing completed
- [ ] Performance baselines established

### Production Configuration

1. **Update application-prod.yml**
   ```yaml
   spring:
     jpa:
       hibernate:
         ddl-auto: validate
     datasource:
       url: jdbc:postgresql://prod-db:5432/ach_rtp_db
       hikari:
         maximum-pool-size: 20
         minimum-idle: 5
   
   logging:
     level:
       root: WARN
       com.example.ach2rtp: INFO
   ```

2. **Update Kubernetes manifests**
   - Set resource limits appropriately
   - Configure replica count (minimum 3)
   - Enable pod disruption budgets
   - Configure network policies

3. **Enable TLS**
   ```bash
   # Create TLS secret
   kubectl create secret tls ach-rtp-tls \
     --cert=path/to/cert.crt \
     --key=path/to/key.key
   ```

4. **Configure Ingress**
   ```yaml
   apiVersion: networking.k8s.io/v1
   kind: Ingress
   metadata:
     name: ach-to-rtp-ingress
   spec:
     tls:
     - hosts:
       - ach-rtp.example.com
         secretName: ach-rtp-tls
     rules:
     - host: ach-rtp.example.com
       http:
         paths:
         - path: /
           pathType: Prefix
           backend:
             service:
               name: ach-to-rtp-service
               port:
                 number: 80
   ```

### Database Migration

```bash
# Run migrations
mvn flyway:migrate -Dflyway.configFiles=src/main/resources/flyway.conf

# Verify schema
psql -h prod-db -U postgres -d ach_rtp_db -c "\dt"
```

## Monitoring and Observability

### Prometheus Metrics

```bash
# Access metrics endpoint
curl http://localhost:8080/api/actuator/prometheus

# Key metrics to monitor:
# - ach_file_uploads_total
# - ach_entries_processed_total
# - rtp_messages_published_total
# - rtp_message_generation_duration_seconds
```

### Grafana Dashboard

1. Add Prometheus data source
2. Import dashboard from `monitoring/grafana-dashboard.json`
3. Configure alerts for critical metrics

### Log Aggregation

```bash
# View logs from all pods
kubectl logs -f deployment/ach-to-rtp-service --all-containers=true

# Stream logs to ELK stack
# Configure Filebeat to collect logs from /app/logs/
```

### Health Checks

```bash
# Liveness probe
curl http://localhost:8080/api/v1/health/live

# Readiness probe
curl http://localhost:8080/api/v1/health/ready

# Full health status
curl http://localhost:8080/api/v1/health/status
```

## Troubleshooting

### Pod won't start

```bash
# Check pod status
kubectl describe pod <pod-name>

# View logs
kubectl logs <pod-name>

# Check events
kubectl get events --sort-by='.lastTimestamp'
```

### Database connection issues

```bash
# Test database connectivity
kubectl exec -it <pod-name> -- psql -h postgres-service -U postgres -d ach_rtp_db -c "SELECT 1"

# Check connection pool
curl http://localhost:8080/api/actuator/metrics/hikaricp.connections
```

### RabbitMQ connection issues

```bash
# Test RabbitMQ connectivity
kubectl exec -it <pod-name> -- curl -i http://rabbitmq-service:15672/api/aliveness-test/

# Check queue status
kubectl exec -it <pod-name> -- curl -u guest:guest http://rabbitmq-service:15672/api/queues
```

### High memory usage

```bash
# Check memory metrics
kubectl top pod <pod-name>

# Increase JVM heap size in deployment
# Add to container env: -Xmx1024m -Xms512m
```

### Slow message processing

```bash
# Check message queue depth
curl -u guest:guest http://localhost:15672/api/queues

# Monitor processing latency
curl http://localhost:8080/api/actuator/metrics/rtp.message.generation.duration
```

## Rollback Procedure

```bash
# Check rollout history
kubectl rollout history deployment/ach-to-rtp-service

# Rollback to previous version
kubectl rollout undo deployment/ach-to-rtp-service

# Rollback to specific revision
kubectl rollout undo deployment/ach-to-rtp-service --to-revision=2

# Verify rollback
kubectl rollout status deployment/ach-to-rtp-service
```

## Backup and Recovery

```bash
# Backup database
pg_dump -h prod-db -U postgres ach_rtp_db > ach_rtp_db.sql

# Restore database
psql -h prod-db -U postgres < ach_rtp_db.sql

# Backup Kubernetes resources
kubectl get all -o yaml > k8s-backup.yaml
```

## Support and Escalation

For issues not covered in this guide:

1. Check application logs: `kubectl logs -f deployment/ach-to-rtp-service`
2. Review Prometheus metrics for anomalies
3. Check Kubernetes events: `kubectl get events`
4. Contact the development team with logs and metrics

## References

- [Spring Boot Deployment Guide](https://spring.io/guides/gs/spring-boot-docker/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [RabbitMQ Deployment Guide](https://www.rabbitmq.com/deployment-guide.html)
- [PostgreSQL Production Setup](https://www.postgresql.org/docs/current/runtime.html)
