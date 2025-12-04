# Docker Setup Guide

This guide provides comprehensive instructions for setting up and running the recruitment platform using Docker Compose.

## Overview

The Docker setup includes the following services:

- **PostgreSQL**: Primary database
- **Redis**: Cache and message broker for Celery
- **Backend**: FastAPI application
- **Celery Worker**: Background task processing
- **Celery Flower**: Monitoring dashboard
- **Nginx**: Reverse proxy and load balancer
- **Frontend**: React/TypeScript application
- **MinIO**: S3-compatible object storage
- **ClamAV**: Virus scanning service
- **Elasticsearch**: Search engine (optional)
- **Kibana**: Search UI (optional)

## Prerequisites

- Docker (version 20.10 or higher)
- Docker Compose (version 1.29 or higher)
- At least 4GB of RAM available
- At least 10GB of disk space

## Quick Start

### 1. Clone and Setup

```bash
# Clone the repository
git clone <repository-url>
cd recruitment-platform

# Navigate to Backend directory
cd Backend

# Copy environment file
cp .env.example .env

# Edit environment variables
nano .env
```

### 2. Configure Environment Variables

Edit the `.env` file with your configuration:

```env
# Database Configuration
DB_USER=recruitment_user
DB_PASSWORD=secure_password

# Redis Configuration
REDIS_PASSWORD=redis_password

# Celery Flower
FLOWER_USER=admin
FLOWER_PASSWORD=admin123

# MinIO Configuration
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=minioadmin123

# JWT Configuration
JWT_SECRET_KEY=your_jwt_secret_key_here
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# Email Configuration (if using email services)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password

# LLM Provider Configuration (if using AI services)
OPENAI_API_KEY=your_openai_key
GEMINI_API_KEY=your_gemini_key
GROQ_API_KEY=your_groq_key
```

### 3. Build and Start Services

```bash
# Build and start all services
docker-compose up --build

# Or run in detached mode
docker-compose up -d --build
```

### 4. Verify Services

```bash
# Check service status
docker-compose ps

# View logs
docker-compose logs -f

# Access applications
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Documentation: http://localhost:8000/docs
# Celery Flower: http://localhost:5555
# MinIO Console: http://localhost:9001
# Kibana (if enabled): http://localhost:5601
```

## Service Details

### Backend Service

- **Port**: 8000
- **Health Check**: `/health` endpoint
- **Environment**: Production-ready with proper logging
- **Features**:
  - FastAPI with automatic API documentation
  - SQLAlchemy ORM with PostgreSQL
  - JWT authentication
  - Rate limiting
  - CORS configuration
  - Request logging

### Frontend Service

- **Port**: 3000
- **Build**: Multi-stage build for production
- **Features**:
  - React/TypeScript application
  - Nginx server with proper caching
  - Client-side routing support
  - Security headers
  - Gzip compression

### Database Service

- **Image**: PostgreSQL 15
- **Port**: 5432
- **Data Persistence**: Named volume `postgres_data`
- **Health Check**: Built-in PostgreSQL health check
- **Configuration**:
  - Database: `recruitment_platform`
  - User: `recruitment_user`
  - Password: From environment variable

### Redis Service

- **Image**: Redis 7
- **Port**: 6379
- **Data Persistence**: Named volume `redis_data`
- **Health Check**: Built-in Redis health check
- **Usage**: Cache and Celery message broker

### Celery Worker

- **Concurrency**: 4 workers
- **Logging**: Info level
- **Health Check**: Monitored through backend service
- **Tasks**: File processing, virus scanning, text extraction

### Celery Flower

- **Port**: 5555
- **Authentication**: Basic auth (admin/admin123 by default)
- **Monitoring**: Real-time task monitoring
- **Access**: http://localhost:5555

### Nginx Reverse Proxy

- **Ports**: 80 (HTTP), 443 (HTTPS - ready for SSL)
- **Features**:
  - Load balancing
  - SSL/TLS support (ready)
  - Rate limiting
  - Gzip compression
  - Security headers
  - Static file serving

### MinIO (Object Storage)

- **Ports**: 9000 (API), 9001 (Console)
- **Default Credentials**: minioadmin/minioadmin123
- **Usage**: File storage for uploaded resumes
- **S3 Compatibility**: Compatible with AWS S3 SDK

### ClamAV (Virus Scanner)

- **Port**: 3310
- **Image**: mkodera/clamav
- **Usage**: File virus scanning
- **Integration**: Automatically scans uploaded files

### Elasticsearch (Optional)

- **Port**: 9200
- **Memory**: 512MB allocated
- **Usage**: Search functionality
- **Integration**: Optional for advanced search features

### Kibana (Optional)

- **Port**: 5601
- **Integration**: Elasticsearch UI
- **Usage**: Search analytics and visualization

## Development Workflow

### Development Mode

```bash
# Start services in development mode
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

# Or use docker-compose override files
docker-compose -f docker-compose.yml -f docker-compose.override.yml up
```

### Adding Services

1. Create a new service in `docker-compose.yml`
2. Add necessary environment variables
3. Update network configuration
4. Add volume mounts if needed
5. Include health checks for production

### Environment-Specific Configurations

Create separate docker-compose files for different environments:

```bash
# Development
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

# Staging
docker-compose -f docker-compose.yml -f docker-compose.staging.yml up

# Production
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up
```

## Common Commands

### Service Management

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# Restart services
docker-compose restart

# View logs
docker-compose logs -f [service_name]

# Execute command in container
docker-compose exec [service_name] [command]

# View resource usage
docker-compose top

# Clean up unused containers
docker-compose down -v --remove-orphans
```

### Database Operations

```bash
# Access database shell
docker-compose exec postgres psql -U recruitment_user -d recruitment_platform

# Run database migrations
docker-compose exec backend python manage.py migrate

# Create database backup
docker-compose exec postgres pg_dump -U recruitment_user recruitment_platform > backup.sql
```

### File Management

```bash
# Access uploaded files
docker-compose exec backend ls -la /app/uploads/

# Access logs
docker-compose exec backend tail -f /app/logs/app.log

# MinIO operations
docker-compose exec minio mc ls minio/recruitment/
```

## Troubleshooting

### Common Issues

1. **Port Conflicts**
   ```bash
   # Check port usage
   netstat -an | grep :8000
   
   # Change ports in docker-compose.yml
   ports:
     - "8080:8000"  # Change backend port
   ```

2. **Database Connection Issues**
   ```bash
   # Check database logs
   docker-compose logs postgres
   
   # Verify database connectivity
   docker-compose exec backend python -c "import sqlalchemy; print('Database OK')"
   ```

3. **Memory Issues**
   ```bash
   # Check memory usage
   docker stats
   
   # Adjust memory limits in docker-compose.yml
   deploy:
     resources:
       limits:
         memory: 1G
   ```

4. **Build Failures**
   ```bash
   # Clean build cache
   docker-compose down -v
   docker system prune -a
   
   # Rebuild
   docker-compose up --build --force-recreate
   ```

### Health Check Failures

```bash
# Check service health
docker-compose ps

# View health check logs
docker-compose logs [service_name]

# Manual health check
curl http://localhost:8000/health
curl http://localhost:3000
```

## Security Considerations

### Production Security

1. **Environment Variables**
   - Use strong, unique passwords
   - Store sensitive data in secrets management
   - Rotate credentials regularly

2. **Network Security**
   - Use private networks for internal services
   - Implement firewall rules
   - Restrict external access to necessary ports

3. **SSL/TLS**
   - Configure SSL certificates
   - Use Let's Encrypt for free certificates
   - Enforce HTTPS redirects

4. **Container Security**
   - Use official, verified images
   - Regularly update base images
   - Scan images for vulnerabilities

### Monitoring and Logging

```bash
# Monitor resource usage
docker-compose top

# View logs
docker-compose logs -f --tail=100

# Set up log aggregation
# Consider using ELK stack or similar for production
```

## Scaling

### Horizontal Scaling

```bash
# Scale backend service
docker-compose up -d --scale backend=3

# Scale Celery workers
docker-compose up -d --scale celery-worker=6
```

### Load Balancing

Nginx automatically handles load balancing across multiple backend instances.

## Backup and Recovery

### Database Backup

```bash
# Create backup
docker-compose exec postgres pg_dump -U recruitment_user recruitment_platform > backup_$(date +%Y%m%d).sql

# Restore backup
docker-compose exec -T postgres psql -U recruitment_user recruitment_platform < backup_20231201.sql
```

### File Storage Backup

```bash
# Backup MinIO data
docker-compose exec minio mc cp --recursive minio/recruitment/ /backups/recruitment/

# Restore MinIO data
docker-compose exec minio mc cp --recursive /backups/recruitment/ minio/recruitment/
```

## Maintenance

### Regular Tasks

1. **Update Images**
   ```bash
   # Pull latest images
   docker-compose pull
   
   # Rebuild and restart
   docker-compose up -d --force-recreate
   ```

2. **Log Rotation**
   - Configure log rotation in Docker
   - Monitor log file sizes
   - Archive old logs

3. **Database Maintenance**
   - Regular vacuuming
   - Index optimization
   - Performance monitoring

### Performance Tuning

1. **Memory Allocation**
   - Adjust JVM heap size for Elasticsearch
   - Configure Redis memory limits
   - Optimize PostgreSQL memory settings

2. **Network Optimization**
   - Use overlay networks for multi-host setups
   - Configure DNS resolution
   - Optimize firewall rules

## Support

For issues and questions:

1. Check this documentation
2. Review Docker logs: `docker-compose logs`
3. Check service health: `docker-compose ps`
4. Monitor resource usage: `docker stats`

## Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://reactjs.org/)