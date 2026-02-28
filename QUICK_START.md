# Quick Start Guide

## 5-Minute Setup

### 1. Prerequisites Check
```bash
java -version          # Should be 17+
mvn -version          # Should be 3.9+
docker --version      # Should be latest
docker-compose --version
```

### 2. Start Dependencies
```bash
cd ach-to-rtp-service
docker-compose up -d
```

### 3. Build Application
```bash
mvn clean package
```

### 4. Run Application
```bash
mvn spring-boot:run
```

### 5. Verify Installation
```bash
curl http://localhost:8080/api/v1/health/status
# Expected response: {"status":"UP","service":"ach-to-rtp-service",...}
```

## Testing the Service

### Upload Sample ACH File
```bash
curl -X POST \
  -F "file=@test-data/sample.ach" \
  http://localhost:8080/api/v1/conversion/upload
```

### Check Job Status
```bash
curl http://localhost:8080/api/v1/jobs/{jobId}
```

### View Health Status
```bash
curl http://localhost:8080/api/v1/health/status
curl http://localhost:8080/api/v1/health/live
curl http://localhost:8080/api/v1/health/ready
```

## Common Commands

### Development
```bash
# Run tests
mvn test

# Run with debug
mvn spring-boot:run -Dspring-boot.run.jvmArguments="-Xdebug -Xrunjdwp:transport=dt_socket,server=y,suspend=y,address=5005"

# Check code coverage
mvn clean test jacoco:report
open target/site/jacoco/index.html
```

### Docker
```bash
# Build image
docker build -t ach-to-rtp-service:1.0.0 .

# Run container
docker run -d -p 8080:8080 ach-to-rtp-service:1.0.0

# View logs
docker logs -f ach-to-rtp-service

# Stop container
docker stop ach-to-rtp-service
```

### Kubernetes
```bash
# Deploy to cluster
kubectl apply -f k8s/

# Check deployment
kubectl get pods -l app=ach-to-rtp-service

# View logs
kubectl logs -f deployment/ach-to-rtp-service

# Port forward
kubectl port-forward svc/ach-to-rtp-service 8080:80
```

## Troubleshooting

### Port Already in Use
```bash
# Kill process on port 8080
lsof -ti:8080 | xargs kill -9
```

### Database Connection Error
```bash
# Check PostgreSQL
docker ps | grep postgres
docker logs postgres

# Restart PostgreSQL
docker restart postgres
```

### RabbitMQ Connection Error
```bash
# Check RabbitMQ
docker ps | grep rabbitmq
docker logs rabbitmq

# Restart RabbitMQ
docker restart rabbitmq
```

### Build Failures
```bash
# Clean rebuild
mvn clean install -U

# Skip tests
mvn clean package -DskipTests
```

## API Quick Reference

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/v1/conversion/upload` | POST | Upload ACH file |
| `/v1/jobs/{jobId}` | GET | Get job status |
| `/v1/jobs` | GET | List jobs |
| `/v1/health/status` | GET | Service status |

## Configuration

### Environment Variables
```bash
export DATABASE_URL=jdbc:postgresql://localhost:5432/ach_rtp_db
export DATABASE_USERNAME=postgres
export DATABASE_PASSWORD=postgres
export RABBITMQ_HOST=localhost
export RABBITMQ_PORT=5672
export RABBITMQ_USERNAME=guest
export RABBITMQ_PASSWORD=guest
```

### Application Properties
Edit `src/main/resources/application.yml`:
```yaml
ach:
  max-file-size: 10485760
  max-entries-per-batch: 10000

rtp:
  message-timeout-ms: 30000

mq:
  exchange-name: rtp-gateway
  routing-key: rtp.credit.transfer
```

## Next Steps

1. Read [README.md](README.md) for detailed overview
2. Review [API.md](API.md) for endpoint documentation
3. Check [DEPLOYMENT.md](DEPLOYMENT.md) for production setup
4. Study [ARCHITECTURE.md](ARCHITECTURE.md) for technical details
5. Follow [CONTRIBUTING.md](CONTRIBUTING.md) for development

## Support

- **Documentation:** See README.md and other .md files
- **Issues:** Check TROUBLESHOOTING section in README.md
- **Development:** See CONTRIBUTING.md
- **Architecture:** See ARCHITECTURE.md

---

Happy coding! 🚀
