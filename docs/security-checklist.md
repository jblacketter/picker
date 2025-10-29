# Security Checklist for Production Deployment

## Critical Security Issues Identified

### 🔴 HIGH PRIORITY - Must Fix Before Production

1. **DEBUG Mode**
   - **Current:** `DEBUG = True` (default)
   - **Issue:** Exposes sensitive information, stack traces, and settings
   - **Fix:** Set `DEBUG=False` in production `.env`

2. **SQLite Database**
   - **Current:** Using SQLite
   - **Issue:** Not suitable for production with concurrent users, no connection pooling
   - **Fix:** Migrate to PostgreSQL

3. **HTTPS/SSL Settings Missing**
   - **Issue:** No SSL/TLS security headers configured
   - **Fix:** Add SSL security settings (see below)

4. **Session Security**
   - **Issue:** Cookies not marked as secure, vulnerable to interception
   - **Fix:** Configure secure session/CSRF cookies

5. **ALLOWED_HOSTS**
   - **Current:** Defaults to localhost
   - **Issue:** Must specify production domain
   - **Fix:** Set your actual domain in `.env`

### 🟡 MEDIUM PRIORITY - Should Fix

6. **Log File Rotation**
   - **Issue:** Logs will grow indefinitely
   - **Fix:** Implement log rotation

7. **Rate Limiting**
   - **Issue:** No rate limiting on AI API calls
   - **Fix:** Add rate limiting middleware

8. **Admin Panel Exposure**
   - **Issue:** Admin at `/admin/` with default credentials
   - **Fix:** Change admin URL, strong passwords

### 🟢 LOW PRIORITY - Nice to Have

9. **API Key Exposure in Logs**
   - **Issue:** Potentially logs API keys
   - **Fix:** Add sanitization for sensitive data

10. **CORS Configuration**
    - **Issue:** Not configured (needed if adding external frontend)
    - **Fix:** Add django-cors-headers if needed

---

## Security Configuration for Production

### 1. Environment Variables (.env)

```bash
# Django Settings - PRODUCTION
SECRET_KEY=generate-a-new-strong-secret-key-here-use-django-secret-key-generator
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database - PostgreSQL
DATABASE_URL=postgresql://picker_user:strong_password@localhost:5432/picker_db

# AI Service
ANTHROPIC_API_KEY=sk-ant-your-production-key
USE_STUB_AI=False

# Security
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

### 2. Update settings.py for Production

Add these security settings to `config/settings.py`:

```python
# Security Settings for Production
if not DEBUG:
    # HTTPS/SSL
    SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', default=True, cast=bool)
    SESSION_COOKIE_SECURE = config('SESSION_COOKIE_SECURE', default=True, cast=bool)
    CSRF_COOKIE_SECURE = config('CSRF_COOKIE_SECURE', default=True, cast=bool)
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'

    # HSTS (HTTP Strict Transport Security)
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

    # Secure proxy header (if behind nginx/apache)
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Database Configuration
import dj_database_url

DATABASES = {
    'default': dj_database_url.config(
        default=config('DATABASE_URL', default='sqlite:///db.sqlite3'),
        conn_max_age=600,
        conn_health_checks=True,
    )
}
```

### 3. Additional Required Packages

Add to `requirements.txt`:

```
dj-database-url>=2.1.0
psycopg2-binary>=2.9.9  # Already included
gunicorn>=21.2.0
whitenoise>=6.6.0  # For static file serving
```

### 4. Generate Strong SECRET_KEY

```bash
# Generate a new secret key
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

---

## Database Security

### PostgreSQL Setup

```bash
# Create database and user
sudo -u postgres psql

CREATE DATABASE picker_db;
CREATE USER picker_user WITH PASSWORD 'strong_random_password_here';
ALTER ROLE picker_user SET client_encoding TO 'utf8';
ALTER ROLE picker_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE picker_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE picker_db TO picker_user;
\q
```

### SQLite Security (NOT for production)

If you must use SQLite in production:
- Set proper file permissions: `chmod 640 db.sqlite3`
- Ensure web server user owns the file
- ⚠️ **Not recommended for multi-user production environments**

---

## Web Server Configuration

### Nginx Configuration (Recommended)

```nginx
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    # SSL Security
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Static files
    location /static/ {
        alias /var/www/picker/staticfiles/;
        expires 30d;
    }

    # Media files
    location /media/ {
        alias /var/www/picker/media/;
        expires 30d;
    }

    # Django application
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## User Authentication Security

### Admin Account Security

```bash
# Change default admin credentials
python manage.py changepassword admin

# Or create new superuser
python manage.py createsuperuser
```

**Password Requirements:**
- Minimum 12 characters
- Mix of uppercase, lowercase, numbers, symbols
- Not based on personal information
- Use a password manager

### Change Admin URL (Security by Obscurity)

In `config/urls.py`:
```python
urlpatterns = [
    path("secret-admin-panel-xyz123/", admin.site.urls),  # Change this!
    # ... other patterns
]
```

---

## API Key Security

### Anthropic API Key

1. **Never commit** API keys to git
2. **Rotate keys** regularly
3. **Monitor usage** in Anthropic console
4. **Set rate limits** in code

### Environment Variable Security

```bash
# Set proper .env permissions
chmod 600 .env
chown picker_user:picker_user .env
```

---

## Logging Security

### Configure Log Rotation

Create `/etc/logrotate.d/picker`:

```
/var/www/picker/logs/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 picker_user picker_user
    sharedscripts
    postrotate
        systemctl reload picker
    endscript
}
```

### Sanitize Sensitive Data in Logs

Update `config/settings.py`:

```python
# Filter sensitive data from logs
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        },
    },
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'picker.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'filters': ['require_debug_false'],
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'mail_admins'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

---

## Firewall Configuration

### UFW (Ubuntu Firewall)

```bash
# Enable firewall
sudo ufw enable

# Allow SSH
sudo ufw allow 22/tcp

# Allow HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Allow PostgreSQL (only from localhost)
sudo ufw allow from 127.0.0.1 to any port 5432

# Check status
sudo ufw status
```

---

## Backup Strategy

### Database Backups

```bash
# Create backup script: /usr/local/bin/backup-picker.sh

#!/bin/bash
BACKUP_DIR="/var/backups/picker"
DATE=$(date +%Y%m%d_%H%M%S)

# Database backup
pg_dump picker_db -U picker_user > "$BACKUP_DIR/db_$DATE.sql"

# Compress
gzip "$BACKUP_DIR/db_$DATE.sql"

# Keep only last 30 days
find $BACKUP_DIR -name "db_*.sql.gz" -mtime +30 -delete
```

```bash
# Schedule daily backups
sudo crontab -e
0 2 * * * /usr/local/bin/backup-picker.sh
```

---

## Monitoring & Alerts

### Set Up Monitoring

1. **Application Monitoring**
   - Consider: Sentry for error tracking
   - Monitor: Response times, error rates

2. **System Monitoring**
   - CPU, Memory, Disk usage
   - PostgreSQL connections
   - Log for suspicious activity

3. **Security Monitoring**
   - Failed login attempts
   - Unusual API usage patterns
   - File integrity monitoring

---

## Pre-Deployment Checklist

### Before Going Live

- [ ] `DEBUG=False` in production `.env`
- [ ] Strong `SECRET_KEY` generated and set
- [ ] `ALLOWED_HOSTS` set to production domain
- [ ] PostgreSQL configured and tested
- [ ] All security headers enabled
- [ ] SSL certificate installed and tested
- [ ] Admin URL changed from `/admin/`
- [ ] Strong admin password set
- [ ] `.env` file permissions set to 600
- [ ] Firewall configured
- [ ] Log rotation configured
- [ ] Database backups scheduled
- [ ] Static files collected: `python manage.py collectstatic`
- [ ] Migrations applied: `python manage.py migrate`
- [ ] Dependencies updated: `pip install -r requirements.txt`
- [ ] Gunicorn/systemd service tested
- [ ] Nginx configuration tested
- [ ] HTTPS redirect working
- [ ] Rate limiting configured
- [ ] Monitoring/alerts set up

### Testing Checklist

- [ ] Test with `DEBUG=False` locally first
- [ ] Run Django security check: `python manage.py check --deploy`
- [ ] Test all major features in staging
- [ ] Verify SSL certificate (https://www.ssllabs.com/ssltest/)
- [ ] Test backup and restore procedures
- [ ] Load testing with expected traffic
- [ ] Penetration testing (if handling sensitive data)

---

## Regular Security Maintenance

### Weekly
- Review logs for suspicious activity
- Check disk space and log sizes
- Verify backups completed successfully

### Monthly
- Update dependencies: `pip install --upgrade -r requirements.txt`
- Review API usage and costs
- Rotate API keys

### Quarterly
- Review and update security policies
- Audit user accounts
- Test disaster recovery procedures
- Security scan with OWASP ZAP or similar

---

## Emergency Procedures

### If API Key is Compromised

1. **Immediately** regenerate key in Anthropic console
2. Update production `.env` file
3. Restart application
4. Review recent API usage for suspicious activity
5. Check logs for unauthorized access

### If System is Compromised

1. **Immediately** take site offline
2. Preserve logs and evidence
3. Identify and patch vulnerability
4. Restore from clean backup
5. Rotate all secrets (SECRET_KEY, DB passwords, API keys)
6. Notify users if data was compromised (legal requirement)

---

## Additional Resources

- [Django Deployment Checklist](https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Mozilla SSL Configuration Generator](https://ssl-config.mozilla.org/)
- [Let's Encrypt SSL Certificates](https://letsencrypt.org/)
- [Django Security Documentation](https://docs.djangoproject.com/en/5.0/topics/security/)
