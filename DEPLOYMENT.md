# WebQx Healthcare Platform - Production Deployment Guide

## 🚀 Production Deployment

### Prerequisites

- Docker and Docker Compose
- PostgreSQL database
- Redis server
- SSL certificates (Let's Encrypt recommended)
- Domain name configured with DNS

### Backend Deployment (Django)

1. **Environment Configuration**

Create `.env` file in backend directory:

```env
# Django Configuration
DJANGO_SECRET_KEY=your-super-secret-key-here
DEBUG=False
ALLOWED_HOSTS=api.webqx.healthcare,localhost

# Database
DB_NAME=webqx_healthcare_prod
DB_USER=webqx_user
DB_PASSWORD=secure-database-password
DB_HOST=postgres
DB_PORT=5432

# Redis
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# OpenEMR Integration
OPENEMR_BASE_URL=https://your-openemr-instance.com
OPENEMR_API_TOKEN=your-openemr-api-token
OPENEMR_CLIENT_ID=your-client-id
OPENEMR_CLIENT_SECRET=your-client-secret

# Telehealth
ZOOM_API_KEY=your-zoom-api-key
ZOOM_API_SECRET=your-zoom-api-secret
JITSI_SERVER_URL=https://meet.jit.si

# Notifications
FIREBASE_CREDENTIALS_PATH=/app/firebase-credentials.json
TWILIO_ACCOUNT_SID=your-twilio-sid
TWILIO_AUTH_TOKEN=your-twilio-token

# Security
SSL_REDIRECT=True
SECURE_PROXY_SSL_HEADER=HTTP_X_FORWARDED_PROTO,https
```

2. **Docker Configuration**

Create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: webqx_healthcare_prod
      POSTGRES_USER: webqx_user
      POSTGRES_PASSWORD: secure-database-password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    restart: unless-stopped

  web:
    build: 
      context: ./backend
      dockerfile: Dockerfile.prod
    command: gunicorn webqx.wsgi:application --bind 0.0.0.0:8000
    volumes:
      - static_volume:/app/staticfiles
      - media_volume:/app/media
    env_file:
      - ./backend/.env
    depends_on:
      - postgres
      - redis
    restart: unless-stopped

  nginx:
    build: ./nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - static_volume:/app/staticfiles
      - media_volume:/app/media
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - web
    restart: unless-stopped

  celery:
    build: ./backend
    command: celery -A webqx worker -l info
    volumes:
      - media_volume:/app/media
    env_file:
      - ./backend/.env
    depends_on:
      - postgres
      - redis
    restart: unless-stopped

  celery-beat:
    build: ./backend
    command: celery -A webqx beat -l info
    env_file:
      - ./backend/.env
    depends_on:
      - postgres
      - redis
    restart: unless-stopped

volumes:
  postgres_data:
  static_volume:
  media_volume:
```

3. **Production Dockerfile**

Create `backend/Dockerfile.prod`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput

# Create non-root user
RUN adduser --disabled-password --gecos '' appuser
RUN chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

CMD ["gunicorn", "webqx.wsgi:application", "--bind", "0.0.0.0:8000"]
```

### Frontend Deployment (React Native)

1. **Build for Production**

```bash
cd frontend

# Install dependencies
npm install

# Build for web (if needed)
expo build:web

# Build APK for Android
expo build:android

# Build IPA for iOS
expo build:ios
```

2. **Environment Configuration**

Create `frontend/.env.production`:

```env
API_BASE_URL=https://api.webqx.healthcare/api
EXPO_PUBLIC_API_URL=https://api.webqx.healthcare/api
```

### Nginx Configuration

Create `nginx/nginx.conf`:

```nginx
upstream web {
    server web:8000;
}

server {
    listen 80;
    server_name api.webqx.healthcare;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.webqx.healthcare;

    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;

    location / {
        proxy_pass http://web;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Host $host;
        proxy_redirect off;
    }

    location /static/ {
        alias /app/staticfiles/;
    }

    location /media/ {
        alias /app/media/;
    }

    client_max_body_size 100M;
}
```

### Security Configuration

1. **SSL/TLS Setup**

```bash
# Using Let's Encrypt
certbot certonly --webroot -w /var/www/html -d api.webqx.healthcare
```

2. **Firewall Configuration**

```bash
# UFW setup
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable
```

### Database Setup

1. **Initial Migration**

```bash
docker-compose -f docker-compose.prod.yml run web python manage.py migrate
```

2. **Create Superuser**

```bash
docker-compose -f docker-compose.prod.yml run web python manage.py createsuperuser
```

### Monitoring and Logging

1. **Application Monitoring**

```yaml
# Add to docker-compose.prod.yml
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml

  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
```

2. **Log Aggregation**

```yaml
# Add to docker-compose.prod.yml
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.11.0
    environment:
      - discovery.type=single-node
      - "ES_JAVA_OPTS=-Xms512m -Xmx512m"

  kibana:
    image: docker.elastic.co/kibana/kibana:8.11.0
    ports:
      - "5601:5601"
    depends_on:
      - elasticsearch
```

### Backup Strategy

1. **Database Backup**

```bash
#!/bin/bash
# backup-db.sh
DATE=$(date +%Y%m%d_%H%M%S)
docker-compose -f docker-compose.prod.yml exec postgres pg_dump -U webqx_user webqx_healthcare_prod > backup_$DATE.sql
```

2. **Media Files Backup**

```bash
#!/bin/bash
# backup-media.sh
DATE=$(date +%Y%m%d_%H%M%S)
tar -czf media_backup_$DATE.tar.gz media/
```

### Deployment Script

Create `deploy.sh`:

```bash
#!/bin/bash
set -e

echo "🚀 Deploying WebQx Healthcare Platform..."

# Pull latest changes
git pull origin main

# Build and start services
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d

# Run migrations
docker-compose -f docker-compose.prod.yml run web python manage.py migrate

# Collect static files
docker-compose -f docker-compose.prod.yml run web python manage.py collectstatic --noinput

# Health check
sleep 30
curl -f http://localhost/api/auth/ || exit 1

echo "✅ Deployment complete!"
```

### Mobile App Distribution

1. **Android (Google Play Store)**

```bash
# Build release APK
expo build:android --type=app-bundle

# Upload to Google Play Console
```

2. **iOS (Apple App Store)**

```bash
# Build release IPA
expo build:ios --type=archive

# Upload to App Store Connect
```

### Maintenance

1. **Regular Updates**

```bash
# Update dependencies
pip list --outdated
npm outdated

# Apply security patches
apt update && apt upgrade
```

2. **Performance Monitoring**

- Monitor database performance
- Check API response times
- Monitor server resources
- Review application logs

### Troubleshooting

1. **Common Issues**

```bash
# Check container logs
docker-compose logs web
docker-compose logs postgres

# Database connection issues
docker-compose exec postgres psql -U webqx_user -d webqx_healthcare_prod

# Clear cache
docker-compose exec redis redis-cli FLUSHALL
```

2. **Health Checks**

```bash
# API health check
curl https://api.webqx.healthcare/api/auth/

# Database health
docker-compose exec postgres pg_isready

# Redis health
docker-compose exec redis redis-cli ping
```

This deployment guide ensures a production-ready setup with security, monitoring, and scalability considerations.