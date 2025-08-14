# Docker Deployment Guide

This guide covers deploying the CEFR Speaking Exam Simulator using Docker and Docker Compose.

## Prerequisites

- **Docker CLI** (Docker Desktop prohibited by organization policy)
- **Colima** for container runtime
- **Docker Compose** for multi-service orchestration

## Quick Start

### 1. Build the Image

```bash
# Build the Docker image
./scripts/build.sh

# Or manually
docker build -t speak-check:latest .
```

### 2. Run with Docker Compose

```bash
# Start all services (app + MongoDB)
./scripts/run-docker.sh

# Or manually
docker-compose up --build -d
```

### 3. Access the Application

- **App**: http://localhost:8501
- **MongoDB**: localhost:27017

## Environment Configuration

### Create Environment File

Copy the template and fill in your API keys:

```bash
cp .env.docker .env.docker.local
# Edit .env.docker.local with your actual keys
```

### Required Environment Variables

```bash
# OpenAI API Key (required for STT and AI assessment)
OPENAI_API_KEY=sk-...

# MongoDB Configuration
MONGODB_URI=mongodb://mongo:27017
MONGODB_DB=speak_check

# GitHub Personal Access Token (for MCP features)
GITHUB_PERSONAL_ACCESS_TOKEN=ghp_...
```

## Development vs Production

### Development (Docker Compose)

```bash
# Start development environment
docker-compose up --build

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Production (Single Container)

```bash
# Build production image
docker build -f Dockerfile.prod -t speak-check:prod .

# Run production container
docker run -d \
  --name speak-check-prod \
  -p 8501:8501 \
  --env-file .env.docker \
  speak-check:prod
```

## Service Management

### Useful Commands

```bash
# View running services
docker-compose ps

# View logs
docker-compose logs -f app
docker-compose logs -f mongo

# Restart services
docker-compose restart

# Access MongoDB shell
docker-compose exec mongo mongosh speak_check

# Access app container
docker-compose exec app bash
```

### Health Checks

Both services include health checks:

- **App**: `curl http://localhost:8501/_stcore/health`
- **MongoDB**: `mongosh --eval "db.adminCommand('ping')"`

## Data Persistence

### Volumes

- **MongoDB Data**: `mongo_data` (persistent)
- **App Data**: `./data` (mounted from host)
- **Logs**: `./logs` (mounted from host)

### Backup MongoDB

```bash
# Create backup
docker-compose exec mongo mongodump --db speak_check --out /data/backup

# Restore backup
docker-compose exec mongo mongorestore --db speak_check /data/backup/speak_check
```

## Troubleshooting

### Common Issues

1. **Port Already in Use**
   ```bash
   # Check what's using port 8501
   lsof -i :8501
   
   # Stop conflicting service or change port in docker-compose.yml
   ```

2. **Permission Issues**
   ```bash
   # Fix data directory permissions
   sudo chown -R $USER:$USER data/ logs/
   ```

3. **MongoDB Connection Issues**
   ```bash
   # Check MongoDB status
   docker-compose exec mongo mongosh --eval "db.adminCommand('ping')"
   
   # View MongoDB logs
   docker-compose logs mongo
   ```

4. **Environment Variables Not Loading**
   ```bash
   # Verify .env.docker exists and has correct format
   cat .env.docker
   
   # Check if variables are loaded
   docker-compose exec app env | grep -E "(OPENAI|MONGO|GITHUB)"
   ```

### Debug Mode

```bash
# Run with debug output
docker-compose up --build

# Access container for debugging
docker-compose exec app bash
```

## Security Considerations

- ✅ Non-root user in containers
- ✅ Health checks implemented
- ✅ Environment variables for secrets
- ✅ Minimal base image (python:3.11-slim)
- ✅ No sensitive data in image layers

## Performance Optimization

### Production Settings

- Use `Dockerfile.prod` for optimized builds
- Enable Docker BuildKit for faster builds
- Use multi-stage builds to reduce image size
- Implement proper health checks

### Resource Limits

```yaml
# Add to docker-compose.yml for production
services:
  app:
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '0.5'
```

## CI/CD Integration

The repository includes GitHub Actions workflow (`.github/workflows/docker.yml`) that:

- Builds Docker images on push/PR
- Tests both development and production images
- Validates health endpoints
- Ensures containerization works correctly

## Monitoring

### Logs

```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f app
```

### Metrics

- Container resource usage: `docker stats`
- Service health: `docker-compose ps`
- Application logs: Streamlit logs in container

## Next Steps

- [ ] Set up reverse proxy (nginx) for SSL termination
- [ ] Configure monitoring and alerting
- [ ] Implement automated backups
- [ ] Set up Kubernetes deployment
- [ ] Add performance benchmarking

## Support

For issues related to Docker deployment:

1. Check the troubleshooting section above
2. Review container logs: `docker-compose logs`
3. Verify environment configuration
4. Ensure Colima is running: `colima status`
