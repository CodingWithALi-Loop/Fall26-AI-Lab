# Deployment Guide

This guide covers deploying the Hadith Search Engine to production environments.

## Table of Contents

1. [Production Checklist](#production-checklist)
2. [Server Setup](#server-setup)
3. [Environment Configuration](#environment-configuration)
4. [Deployment Methods](#deployment-methods)
5. [Security](#security)
6. [Monitoring](#monitoring)
7. [Troubleshooting](#troubleshooting)

---

## Production Checklist

- [ ] Update `SECRET_KEY` in configuration
- [ ] Set `DEBUG = False`
- [ ] Use HTTPS (SSL/TLS certificate)
- [ ] Set environment variables
- [ ] Use production WSGI server (Gunicorn/uWSGI)
- [ ] Configure reverse proxy (Nginx/Apache)
- [ ] Set up logging and monitoring
- [ ] Configure database backups
- [ ] Set up error tracking (Sentry)
- [ ] Test with production data
- [ ] Monitor performance metrics

---

## Server Setup

### Requirements

- Python 3.8+
- Virtual Environment
- Production WSGI server (Gunicorn recommended)
- Reverse proxy (Nginx recommended)
- SSL certificate (Let's Encrypt recommended)

### Installation on Ubuntu/Debian

```bash
# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Install Python and dependencies
sudo apt-get install python3 python3-pip python3-venv nginx -y

# Install Gunicorn
pip install gunicorn

# Create application directory
sudo mkdir -p /var/www/hadith-search
cd /var/www/hadith-search

# Clone/upload application files
# (Upload your application files here)

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
```

### Installation on CentOS/RHEL

```bash
# Update system
sudo yum update -y

# Install Python and dependencies
sudo yum install python3 python3-pip nginx -y

# Install Gunicorn
pip install gunicorn

# Create application directory
sudo mkdir -p /var/www/hadith-search
cd /var/www/hadith-search
```

---

## Environment Configuration

### Create .env File

```bash
cp .env.example .env
nano .env
```

### Update Configuration

```env
# Production settings
FLASK_ENV=production
FLASK_DEBUG=False

# Security
SECRET_KEY=generate-a-random-string-here

# SSL/TLS
SESSION_COOKIE_SECURE=True
SESSION_COOKIE_HTTPONLY=True
SESSION_COOKIE_SAMESITE=Strict

# Server
FLASK_HOST=0.0.0.0
FLASK_PORT=8000

# Logging
LOG_LEVEL=INFO
LOG_FILE=/var/log/hadith-search/app.log
```

### Generate Secret Key

```python
import secrets
print(secrets.token_urlsafe(32))
```

---

## Deployment Methods

### Method 1: Gunicorn + Nginx

#### 1. Configure Gunicorn

Create `/var/www/hadith-search/gunicorn_config.py`:

```python
import multiprocessing

# Server socket
bind = '127.0.0.1:8000'
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = 'sync'
worker_connections = 1000
timeout = 30
keepalive = 2

# Logging
accesslog = '/var/log/hadith-search/access.log'
errorlog = '/var/log/hadith-search/error.log'
loglevel = 'info'

# Process naming
proc_name = 'hadith-search'

# Server mechanics
daemon = False
pidfile = '/var/run/hadith-search.pid'
umask = 0
tmp_upload_dir = None

# SSL/TLS (if needed)
# keyfile = '/path/to/keyfile'
# certfile = '/path/to/certfile'
```

#### 2. Create Systemd Service File

Create `/etc/systemd/system/hadith-search.service`:

```ini
[Unit]
Description=Hadith Search Engine
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/hadith-search
Environment="PATH=/var/www/hadith-search/venv/bin"
ExecStart=/var/www/hadith-search/venv/bin/gunicorn \
    --config /var/www/hadith-search/gunicorn_config.py \
    --access-logfile /var/log/hadith-search/access.log \
    --error-logfile /var/log/hadith-search/error.log \
    app:app

# Auto-restart on failure
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### 3. Enable and Start Service

```bash
# Enable service
sudo systemctl enable hadith-search

# Start service
sudo systemctl start hadith-search

# Check status
sudo systemctl status hadith-search

# View logs
sudo journalctl -u hadith-search -f
```

#### 4. Configure Nginx

Create `/etc/nginx/sites-available/hadith-search`:

```nginx
upstream hadith_search {
    server 127.0.0.1:8000;
}

# HTTP to HTTPS redirect
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    return 301 https://$server_name$request_uri;
}

# HTTPS server
server {
    listen 443 ssl http2;
    server_name your-domain.com www.your-domain.com;

    # SSL certificates
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Proxy settings
    location / {
        proxy_pass http://hadith_search;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 30s;
    }

    # Static files
    location /static/ {
        alias /var/www/hadith-search/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Gzip compression
    gzip on;
    gzip_types text/plain text/css text/xml text/javascript 
               application/x-javascript application/xml+rss 
               application/json application/javascript;
    gzip_vary on;
    gzip_min_length 1000;
}
```

Enable the site:

```bash
sudo ln -s /etc/nginx/sites-available/hadith-search /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Method 2: Docker Deployment

Create `Dockerfile`:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create non-root user
RUN useradd -m -u 1000 hadith && chown -R hadith:hadith /app
USER hadith

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/ || exit 1

# Run application
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "app:app"]
```

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  hadith-search:
    build: .
    ports:
      - "5000:8000"
    environment:
      - FLASK_ENV=production
      - SECRET_KEY=${SECRET_KEY}
    volumes:
      - ./cleaned_hadith.csv:/app/cleaned_hadith.csv
      - ./faiss_index.faiss:/app/faiss_index.faiss
      - ./logs:/app/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/"]
      interval: 30s
      timeout: 3s
      retries: 3

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - hadith-search
    restart: unless-stopped
```

Build and run:

```bash
docker-compose build
docker-compose up -d
```

---

## Security

### 1. SSL/TLS Certificate

Using Let's Encrypt:

```bash
# Install Certbot
sudo apt-get install certbot python3-certbot-nginx -y

# Get certificate
sudo certbot certonly --nginx -d your-domain.com -d www.your-domain.com

# Auto-renewal
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer
```

### 2. Firewall Configuration

```bash
# UFW (Ubuntu)
sudo ufw enable
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
```

### 3. Security Headers

Already configured in Nginx template above.

### 4. Database Security

If using database:

```sql
-- Create non-root user
CREATE USER 'hadith_user'@'localhost' IDENTIFIED BY 'strong-password';
GRANT SELECT ON hadith_db.* TO 'hadith_user'@'localhost';
FLUSH PRIVILEGES;
```

---

## Monitoring

### 1. Application Monitoring

Set up Sentry for error tracking:

```python
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

sentry_sdk.init(
    dsn="your-sentry-dsn",
    integrations=[FlaskIntegration()],
    traces_sample_rate=0.1
)
```

### 2. Performance Monitoring

```bash
# Monitor Gunicorn workers
sudo ps aux | grep gunicorn

# Monitor Nginx
sudo nginx -t
sudo systemctl status nginx
```

### 3. Log Monitoring

```bash
# Application logs
tail -f /var/log/hadith-search/app.log

# Access logs
tail -f /var/log/hadith-search/access.log

# System logs
sudo journalctl -u hadith-search -f
```

### 4. Uptime Monitoring

Services like:
- Uptime Robot (uptime-robot.com)
- Pingdom
- StatusPage.io

---

## Backup Strategy

### Backup Data Files

```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/backups/hadith-search"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup
mkdir -p $BACKUP_DIR
tar -czf $BACKUP_DIR/hadith_backup_$DATE.tar.gz \
    /var/www/hadith-search/cleaned_hadith.csv \
    /var/www/hadith-search/faiss_index.faiss

# Keep only last 30 days
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete
```

Schedule with cron:

```bash
# Run daily at 2 AM
0 2 * * * /path/to/backup.sh
```

---

## Troubleshooting

### Service Won't Start

```bash
# Check logs
sudo journalctl -u hadith-search -n 50

# Test configuration
gunicorn --config /var/www/hadith-search/gunicorn_config.py --check-config app:app
```

### High Memory Usage

```python
# Optimize in config.py
workers = 2  # Reduce worker count
worker_connections = 500  # Reduce connections
```

### Nginx 502 Bad Gateway

```bash
# Check Gunicorn is running
sudo systemctl status hadith-search

# Check port is open
sudo netstat -tlnp | grep 8000

# Restart services
sudo systemctl restart hadith-search nginx
```

### SSL Certificate Issues

```bash
# Verify certificate
sudo openssl x509 -in /etc/letsencrypt/live/your-domain.com/cert.pem -text -noout

# Renew certificate manually
sudo certbot renew --force-renewal
```

---

## Performance Optimization

### 1. Enable Caching

```python
from flask_caching import Cache

cache = Cache(app, config={'CACHE_TYPE': 'redis'})

@cache.cached(timeout=300)
def get_filters():
    # ...
```

### 2. Database Indexing

If using database:

```sql
CREATE INDEX idx_book ON hadiths(book);
CREATE INDEX idx_chapter ON hadiths(chapter);
```

### 3. FAISS GPU Acceleration

```bash
pip install faiss-gpu
```

### 4. Load Balancing

Configure multiple Gunicorn instances and use Nginx upstream:

```nginx
upstream hadith_search {
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
    server 127.0.0.1:8003;
}
```

---

## Support

For deployment issues:
- Check logs: `sudo journalctl -u hadith-search -f`
- Review Nginx config: `sudo nginx -T`
- Test connectivity: `curl http://localhost:8000/`

---

**Last Updated**: May 2, 2026  
**Status**: Production Ready ✅
