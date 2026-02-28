# Docker Build Troubleshooting Guide

## Common Docker Build Issues and Solutions

### Issue 1: Platform Compatibility Error

**Error Message:**
```
failed to solve with frontend dockerfile.v0: failed to create LLB definition: 
no match for platform in manifest sha256:...: not found
```

**Cause:** The Docker base image doesn't support your system's platform (e.g., ARM64 on Apple Silicon).

**Solution:**

Option 1: Use standard Linux images (not Alpine):
```dockerfile
# Instead of:
FROM eclipse-temurin:17-jre-alpine

# Use:
FROM eclipse-temurin:17-jre
```

Option 2: Specify platform explicitly:
```bash
docker build --platform linux/amd64 -t ach-to-rtp-service:1.0.0 .
```

Option 3: Use buildx for multi-platform builds:
```bash
docker buildx build --platform linux/amd64,linux/arm64 -t ach-to-rtp-service:1.0.0 .
```

### Issue 2: Out of Disk Space

**Error Message:**
```
no space left on device
```

**Solution:**
```bash
# Clean up Docker resources
docker system prune -a

# Remove dangling images
docker image prune -a

# Check disk usage
docker system df
```

### Issue 3: Maven Dependency Download Fails

**Error Message:**
```
[ERROR] Failed to execute goal on project ach-to-rtp-service: 
Could not transfer artifact...
```

**Solution:**
```bash
# Clear Maven cache and rebuild
rm -rf ~/.m2/repository
docker build --no-cache -t ach-to-rtp-service:1.0.0 .

# Or specify Maven settings
docker build --build-arg MAVEN_OPTS="-Dmaven.wagon.http.ssl.insecure=true" .
```

### Issue 4: Port Already in Use

**Error Message:**
```
Error response from daemon: driver failed programming external connectivity 
on endpoint ach-to-rtp-service: Bind for 0.0.0.0:8080 failed: port is already allocated
```

**Solution:**
```bash
# Find process using port 8080
lsof -i :8080

# Kill the process
kill -9 <PID>

# Or use a different port
docker run -p 8081:8080 ach-to-rtp-service:1.0.0
```

### Issue 5: Docker Daemon Not Running

**Error Message:**
```
Cannot connect to the Docker daemon at unix:///var/run/docker.sock. 
Is the docker daemon running?
```

**Solution:**

On Linux:
```bash
sudo systemctl start docker
```

On Mac:
```bash
# Start Docker Desktop from Applications
open -a Docker
```

On Windows:
```bash
# Start Docker Desktop from Start Menu
```

### Issue 6: Permission Denied

**Error Message:**
```
Got permission denied while trying to connect to the Docker daemon socket
```

**Solution:**
```bash
# Add user to docker group (Linux)
sudo usermod -aG docker $USER
newgrp docker

# Or use sudo
sudo docker build -t ach-to-rtp-service:1.0.0 .
```

## Docker Build Best Practices

### 1. Use .dockerignore

Create `.dockerignore` to exclude unnecessary files:
```
target/
.git/
.idea/
*.log
node_modules/
```

### 2. Multi-Stage Builds

Use multi-stage builds to reduce image size:
```dockerfile
FROM maven:3.9 as builder
RUN mvn clean package

FROM eclipse-temurin:17-jre
COPY --from=builder /build/target/app.jar .
```

### 3. Layer Caching

Order Dockerfile commands to maximize caching:
```dockerfile
# Bad: Changes invalidate all layers
COPY . .
RUN mvn clean package

# Good: Dependencies cached separately
COPY pom.xml .
RUN mvn dependency:resolve
COPY src ./src
RUN mvn clean package
```

### 4. Minimize Image Size

```dockerfile
# Remove unnecessary packages
RUN apt-get update && apt-get install -y curl && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Use smaller base images
FROM eclipse-temurin:17-jre  # ~300MB
# Instead of
FROM openjdk:17               # ~500MB
```

### 5. Security

```dockerfile
# Use non-root user
RUN useradd -m -u 1000 appuser
USER appuser

# Don't run as root
# USER appuser
```

## Docker Compose Issues

### Issue: Services Won't Start

**Solution:**
```bash
# Check service logs
docker-compose logs postgres
docker-compose logs rabbitmq
docker-compose logs ach-to-rtp-service

# Restart services
docker-compose restart

# Rebuild services
docker-compose up --build
```

### Issue: Database Connection Failed

**Solution:**
```bash
# Wait for PostgreSQL to be ready
docker-compose up -d postgres
sleep 10
docker-compose up -d

# Or use depends_on with healthcheck
# (already configured in docker-compose.yml)
```

### Issue: Port Conflicts

**Solution:**
```bash
# Change ports in docker-compose.yml
ports:
  - "8081:8080"  # Use 8081 instead of 8080

# Or stop conflicting containers
docker stop <container_name>
```

## Performance Optimization

### Build Speed

```bash
# Use BuildKit for faster builds
DOCKER_BUILDKIT=1 docker build -t ach-to-rtp-service:1.0.0 .

# Use cache from registry
docker build --cache-from myregistry/ach-to-rtp-service:latest .
```

### Image Size

```bash
# Check image size
docker images ach-to-rtp-service

# Use smaller base images
FROM eclipse-temurin:17-jre-jammy  # Smaller than full JDK
```

### Runtime Performance

```bash
# Set memory limits
docker run -m 512m ach-to-rtp-service:1.0.0

# Set CPU limits
docker run --cpus="1.5" ach-to-rtp-service:1.0.0
```

## Debugging

### View Build Logs

```bash
# Verbose output
docker build --progress=plain -t ach-to-rtp-service:1.0.0 .

# Keep build context for inspection
docker build --keep-state -t ach-to-rtp-service:1.0.0 .
```

### Inspect Container

```bash
# Shell into running container
docker exec -it ach-to-rtp-service /bin/bash

# View container logs
docker logs -f ach-to-rtp-service

# Inspect image
docker inspect ach-to-rtp-service:1.0.0
```

### Test Build Locally

```bash
# Build without pushing
docker build -t ach-to-rtp-service:test .

# Run and test
docker run -it --rm -p 8080:8080 ach-to-rtp-service:test

# Test health check
curl http://localhost:8080/api/v1/health/status
```

## Registry Operations

### Push to Registry

```bash
# Tag image
docker tag ach-to-rtp-service:1.0.0 myregistry.azurecr.io/ach-to-rtp-service:1.0.0

# Login to registry
docker login myregistry.azurecr.io

# Push image
docker push myregistry.azurecr.io/ach-to-rtp-service:1.0.0
```

### Pull from Registry

```bash
# Pull image
docker pull myregistry.azurecr.io/ach-to-rtp-service:1.0.0

# Run from registry
docker run -d -p 8080:8080 myregistry.azurecr.io/ach-to-rtp-service:1.0.0
```

## Useful Commands

```bash
# List images
docker images

# List containers
docker ps -a

# Remove image
docker rmi ach-to-rtp-service:1.0.0

# Remove container
docker rm <container_id>

# Clean up system
docker system prune -a

# Check Docker version
docker version

# Check Docker info
docker info
```

## Getting Help

If you encounter issues not covered here:

1. Check Docker logs: `docker logs <container_name>`
2. Review Docker documentation: https://docs.docker.com/
3. Check image documentation: https://hub.docker.com/_/eclipse-temurin
4. Search Docker forums or Stack Overflow

## References

- [Docker Documentation](https://docs.docker.com/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Eclipse Temurin Images](https://hub.docker.com/_/eclipse-temurin)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
