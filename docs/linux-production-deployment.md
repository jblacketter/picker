# Linux Production Deployment Guide

Complete guide for deploying Picker on a Linux server (Ubuntu 22.04 LTS recommended).

## Prerequisites

- Ubuntu 22.04 LTS server with root/sudo access
- Domain name pointed to your server IP
- SSH access configured
- At least 2GB RAM, 20GB storage

---

## Step 1: Initial Server Setup

### 1.1 Update System

```bash
sudo apt update && sudo apt upgrade -y
```

### 1.2 Create Application User

```bash
# Create dedicated user for the application
sudo adduser picker --disabled-password --gecos ""
sudo usermod -aG sudo picker  # Optional: if you need sudo access

# Switch to picker user
sudo su - picker
```

### 1.3 Install System Dependencies

```bash
sudo apt install -y \
    python3.11 \
    python3.11-venv \
    python3-pip \
    postgresql \
    postgresql-contrib \
    nginx \
    git \
    supervisor \
    ufw \
    certbot \
    python3-certbot-nginx
```

---

## Step 2: PostgreSQL Database Setup

### 2.1 Configure PostgreSQL

```bash
# Switch to postgres user
sudo -u postgres psql

# Create database and user
CREATE DATABASE picker_db;
CREATE USER picker_user WITH PASSWORD 'your_secure_password_here';
ALTER ROLE picker_user SET client_encoding TO 'utf8';
ALTER ROLE picker_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE picker_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE picker_db TO picker_user;

# For PostgreSQL 15+, grant schema permissions
\c picker_db
GRANT ALL ON SCHEMA public TO picker_user;

\q
```

### 2.2 Test Connection

```bash
psql -U picker_user -d picker_db -h localhost
# Enter password when prompted
# If connection works, type \q to exit
```

---

## Step 3: Application Deployment

### 3.1 Create Directory Structure

```bash
# Create application directory
sudo mkdir -p /var/www/picker
sudo chown picker:picker /var/www/picker

# Create log directory
sudo mkdir -p /var/www/picker/logs
sudo chown picker:picker /var/www/picker/logs

# Create backup directory
sudo mkdir -p /var/backups/picker
sudo chown picker:picker /var/backups/picker
```

### 3.2 Clone Repository

```bash
cd /var/www/picker
git clone https://github.com/jblacketter/picker.git .

# If private repo, you'll need to authenticate
# Alternative: use deployment keys or personal access token
```

### 3.3 Set Up Python Virtual Environment

```bash
cd /var/www/picker
python3.11 -m venv .venv
source .venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Install production dependencies
pip install gunicorn dj-database-url whitenoise
```

### 3.4 Configure Environment Variables

```bash
# Copy example environment file
cp .env.example .env

# Edit .env file
nano .env
```

**Production .env configuration:**

```bash
# Django Settings - PRODUCTION
SECRET_KEY=your-generated-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database
DATABASE_URL=postgresql://picker_user:your_secure_password_here@localhost:5432/picker_db

# AI Service
ANTHROPIC_API_KEY=sk-ant-your-production-api-key
USE_STUB_AI=False

# Security
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True

# Email (optional - for error notifications)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password
```

```bash
# Generate a strong SECRET_KEY
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Set proper permissions
chmod 600 .env
chown picker:picker .env
```

---

## Step 4: Django Application Setup

### 4.1 Update settings.py for Production

Add to `config/settings.py`:

```python
import dj_database_url

# Database Configuration
DATABASES = {
    'default': dj_database_url.config(
        default=config('DATABASE_URL', default='sqlite:///db.sqlite3'),
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# Security Settings for Production
if not DEBUG:
    # HTTPS/SSL
    SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', default=True, cast=bool)
    SESSION_COOKIE_SECURE = config('SESSION_COOKIE_SECURE', default=True, cast=bool)
    CSRF_COOKIE_SECURE = config('CSRF_COOKIE_SECURE', default=True, cast=bool)
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'

    # HSTS
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

    # Proxy header
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

    # WhiteNoise for static files
    MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

### 4.2 Run Migrations

```bash
cd /var/www/picker
source .venv/bin/activate

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic --noinput

# Test configuration
python manage.py check --deploy
```

---

## Step 5: Gunicorn Configuration

### 5.1 Test Gunicorn

```bash
cd /var/www/picker
source .venv/bin/activate
gunicorn --bind 0.0.0.0:8000 config.wsgi:application
```

Visit `http://your-server-ip:8000` to test. Press Ctrl+C to stop.

### 5.2 Create Gunicorn Systemd Service

```bash
sudo nano /etc/systemd/system/picker.service
```

```ini
[Unit]
Description=Picker Django Application
After=network.target postgresql.service
Requires=postgresql.service

[Service]
Type=notify
User=picker
Group=picker
WorkingDirectory=/var/www/picker
Environment="PATH=/var/www/picker/.venv/bin"
ExecStart=/var/www/picker/.venv/bin/gunicorn \
    --workers 3 \
    --bind unix:/var/www/picker/picker.sock \
    --timeout 120 \
    --access-logfile /var/www/picker/logs/gunicorn-access.log \
    --error-logfile /var/www/picker/logs/gunicorn-error.log \
    --log-level info \
    config.wsgi:application
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true

[Install]
WantedBy=multi-user.target
```

### 5.3 Start Gunicorn Service

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service to start on boot
sudo systemctl enable picker

# Start service
sudo systemctl start picker

# Check status
sudo systemctl status picker

# View logs
sudo journalctl -u picker -f
```

---

## Step 6: Nginx Configuration

### 6.1 Create Nginx Configuration

```bash
sudo nano /etc/nginx/sites-available/picker
```

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    # Redirect to HTTPS (after SSL is configured)
    # return 301 https://$server_name$request_uri;

    client_max_body_size 10M;

    # Static files
    location /static/ {
        alias /var/www/picker/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Media files
    location /media/ {
        alias /var/www/picker/media/;
        expires 30d;
    }

    # Django application
    location / {
        proxy_pass http://unix:/var/www/picker/picker.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;

        # Timeouts
        proxy_connect_timeout 120s;
        proxy_send_timeout 120s;
        proxy_read_timeout 120s;
    }
}
```

### 6.2 Enable Site and Test

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/picker /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# If test passes, reload nginx
sudo systemctl reload nginx

# Enable nginx to start on boot
sudo systemctl enable nginx
```

---

## Step 7: SSL Certificate (Let's Encrypt)

### 7.1 Install SSL Certificate

```bash
# Obtain certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Follow prompts:
# - Enter email
# - Agree to terms
# - Choose whether to redirect HTTP to HTTPS (recommend: yes)
```

### 7.2 Test SSL Configuration

Visit: https://www.ssllabs.com/ssltest/analyze.html?d=yourdomain.com

### 7.3 Auto-Renewal

```bash
# Test renewal
sudo certbot renew --dry-run

# Certbot automatically sets up cron job for renewal
# Verify with:
sudo systemctl list-timers | grep certbot
```

---

## Step 8: Firewall Configuration

```bash
# Enable firewall
sudo ufw enable

# Allow SSH (IMPORTANT: do this first!)
sudo ufw allow 22/tcp

# Allow HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Deny direct access to Gunicorn
sudo ufw deny 8000

# Check status
sudo ufw status verbose
```

---

## Step 9: Log Rotation

### 9.1 Configure Log Rotation

```bash
sudo nano /etc/logrotate.d/picker
```

```
/var/www/picker/logs/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 picker picker
    sharedscripts
    postrotate
        systemctl reload picker > /dev/null 2>&1 || true
    endscript
}
```

---

## Step 10: Database Backups

### 10.1 Create Backup Script

```bash
sudo nano /usr/local/bin/backup-picker.sh
```

```bash
#!/bin/bash
BACKUP_DIR="/var/backups/picker"
DATE=$(date +%Y%m%d_%H%M%S)
DB_USER="picker_user"
DB_NAME="picker_db"

# Create backup
pg_dump -U $DB_USER $DB_NAME | gzip > "$BACKUP_DIR/db_$DATE.sql.gz"

# Keep only last 30 days
find $BACKUP_DIR -name "db_*.sql.gz" -mtime +30 -delete

# Log backup
echo "$(date): Backup completed - db_$DATE.sql.gz" >> /var/www/picker/logs/backup.log
```

```bash
# Make executable
sudo chmod +x /usr/local/bin/backup-picker.sh

# Test backup
sudo -u picker /usr/local/bin/backup-picker.sh
```

### 10.2 Schedule Daily Backups

```bash
# Edit crontab for picker user
sudo -u picker crontab -e

# Add this line (runs at 2 AM daily)
0 2 * * * /usr/local/bin/backup-picker.sh
```

---

## Step 11: Monitoring Setup

### 11.1 Install and Configure Fail2Ban

```bash
# Install fail2ban
sudo apt install fail2ban -y

# Create custom configuration
sudo nano /etc/fail2ban/jail.local
```

```ini
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5

[sshd]
enabled = true

[nginx-http-auth]
enabled = true

[nginx-noscript]
enabled = true

[nginx-badbots]
enabled = true
```

```bash
# Start fail2ban
sudo systemctl enable fail2ban
sudo systemctl start fail2ban

# Check status
sudo fail2ban-client status
```

### 11.2 Set Up System Monitoring

```bash
# Install monitoring tools
sudo apt install htop iotop nethogs -y

# Optional: Install netdata for web-based monitoring
bash <(curl -Ss https://my-netdata.io/kickstart.sh)
```

---

## Step 12: Final Checks

### 12.1 Verification Checklist

```bash
# 1. Check all services are running
sudo systemctl status picker
sudo systemctl status nginx
sudo systemctl status postgresql

# 2. Test website
curl -I https://yourdomain.com

# 3. Check logs
sudo tail -f /var/www/picker/logs/gunicorn-error.log

# 4. Run Django checks
cd /var/www/picker
source .venv/bin/activate
python manage.py check --deploy

# 5. Test database connection
python manage.py dbshell

# 6. Verify static files
curl https://yourdomain.com/static/admin/css/base.css

# 7. Check firewall
sudo ufw status verbose

# 8. Verify SSL
curl -I https://yourdomain.com | grep -i strict
```

---

## Common Operations

### Update Application Code

```bash
cd /var/www/picker
source .venv/bin/activate

# Pull latest code
git pull origin main

# Install any new dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Restart application
sudo systemctl restart picker
```

### View Logs

```bash
# Application logs
tail -f /var/www/picker/logs/gunicorn-error.log

# System logs
sudo journalctl -u picker -f

# Nginx logs
sudo tail -f /var/log/nginx/error.log
```

### Restart Services

```bash
# Restart Django application
sudo systemctl restart picker

# Restart Nginx
sudo systemctl restart nginx

# Restart PostgreSQL
sudo systemctl restart postgresql
```

---

## Troubleshooting

### Service Won't Start

```bash
# Check service status
sudo systemctl status picker

# View detailed logs
sudo journalctl -u picker -n 50 --no-pager

# Check configuration
gunicorn --check-config config.wsgi:application
```

### Permission Errors

```bash
# Fix ownership
sudo chown -R picker:picker /var/www/picker

# Fix socket permissions
sudo chmod 660 /var/www/picker/picker.sock
```

### Database Connection Issues

```bash
# Test connection
sudo -u picker psql -U picker_user -d picker_db -h localhost

# Check PostgreSQL is running
sudo systemctl status postgresql

# View PostgreSQL logs
sudo tail -f /var/log/postgresql/postgresql-14-main.log
```

### 502 Bad Gateway

```bash
# Check Gunicorn is running
sudo systemctl status picker

# Check socket exists
ls -l /var/www/picker/picker.sock

# Check Nginx error log
sudo tail -f /var/log/nginx/error.log
```

---

## Security Hardening

### Additional Security Steps

```bash
# 1. Disable root SSH login
sudo nano /etc/ssh/sshd_config
# Set: PermitRootLogin no
sudo systemctl restart sshd

# 2. Change SSH port (optional)
# In /etc/ssh/sshd_config, change Port 22 to something else

# 3. Install and configure Tripwire (file integrity)
sudo apt install tripwire -y

# 4. Enable automatic security updates
sudo apt install unattended-upgrades -y
sudo dpkg-reconfigure unattended-upgrades
```

---

## Performance Tuning

### Gunicorn Workers

```bash
# Calculate optimal workers: (2 x CPU cores) + 1
# Check CPU cores
nproc

# Update /etc/systemd/system/picker.service
# For 2 CPU cores: --workers 5
# For 4 CPU cores: --workers 9
```

### PostgreSQL Tuning

```bash
sudo nano /etc/postgresql/14/main/postgresql.conf
```

```ini
# For 2GB RAM server
shared_buffers = 512MB
effective_cache_size = 1536MB
maintenance_work_mem = 128MB
work_mem = 5MB
```

```bash
sudo systemctl restart postgresql
```

---

## Maintenance Schedule

### Daily
- Automatic backups (2 AM)
- Log rotation
- Security updates (if unattended-upgrades enabled)

### Weekly
- Review logs for errors
- Check disk space: `df -h`
- Monitor system resources: `htop`

### Monthly
- Update dependencies: `pip install --upgrade -r requirements.txt`
- Review security logs
- Test backup restoration
- Update system packages: `sudo apt update && sudo apt upgrade`

### Quarterly
- SSL certificate renewal (automatic, but verify)
- Review and optimize database
- Security audit
- Review and update firewall rules

---

## Resources

- [Django Deployment Checklist](https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/)
- [Gunicorn Documentation](https://docs.gunicorn.org/)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Let's Encrypt](https://letsencrypt.org/)
- [UFW Documentation](https://help.ubuntu.com/community/UFW)
