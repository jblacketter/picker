# Apache Production Deployment Guide

Complete guide for deploying Picker with Apache on Linux (Ubuntu 22.04 LTS).

**Note:** This assumes Apache is already installed. Django will run via Gunicorn on an internal port (e.g., 8000) and Apache will proxy requests to it.

---

## Architecture

```
Internet → Apache (Port 80/443) → Gunicorn (Port 8000) → Django Application
```

Apache handles:
- SSL/TLS termination
- Static file serving
- Reverse proxy to Django
- Security headers

---

## Prerequisites

- Apache2 installed and running
- Root/sudo access
- Domain name pointed to your server
- Follow Steps 1-4 from [Linux Production Deployment](linux-production-deployment.md) first

---

## Step 1: Install Required Apache Modules

```bash
# Enable required Apache modules
sudo a2enmod proxy
sudo a2enmod proxy_http
sudo a2enmod ssl
sudo a2enmod headers
sudo a2enmod rewrite

# Restart Apache
sudo systemctl restart apache2
```

---

## Step 2: Set Up Gunicorn (Same as Nginx Guide)

### 2.1 Create Gunicorn Systemd Service

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
    --bind 127.0.0.1:8000 \
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

**Note:** Gunicorn binds to `127.0.0.1:8000` (localhost only, not accessible from outside)

### 2.2 Start Gunicorn

```bash
sudo systemctl daemon-reload
sudo systemctl enable picker
sudo systemctl start picker
sudo systemctl status picker
```

---

## Step 3: Configure Apache Virtual Host

### 3.1 Create Apache Configuration

```bash
sudo nano /etc/apache2/sites-available/picker.conf
```

**For HTTP (before SSL):**

```apache
<VirtualHost *:80>
    ServerName yourdomain.com
    ServerAlias www.yourdomain.com
    ServerAdmin admin@yourdomain.com

    # Logging
    ErrorLog ${APACHE_LOG_DIR}/picker_error.log
    CustomLog ${APACHE_LOG_DIR}/picker_access.log combined

    # Static files - served directly by Apache
    Alias /static /var/www/picker/staticfiles
    <Directory /var/www/picker/staticfiles>
        Require all granted
        ExpiresActive On
        ExpiresDefault "access plus 1 month"
    </Directory>

    # Media files
    Alias /media /var/www/picker/media
    <Directory /var/www/picker/media>
        Require all granted
        ExpiresActive On
        ExpiresDefault "access plus 1 month"
    </Directory>

    # Proxy to Gunicorn
    ProxyPreserveHost On
    ProxyPass /static !
    ProxyPass /media !
    ProxyPass / http://127.0.0.1:8000/
    ProxyPassReverse / http://127.0.0.1:8000/

    # Security headers
    Header always set X-Frame-Options "DENY"
    Header always set X-Content-Type-Options "nosniff"
    Header always set X-XSS-Protection "1; mode=block"
</VirtualHost>
```

### 3.2 Enable Site

```bash
# Disable default site (optional)
sudo a2dissite 000-default.conf

# Enable picker site
sudo a2ensite picker.conf

# Test configuration
sudo apache2ctl configtest

# Restart Apache
sudo systemctl restart apache2
```

---

## Step 4: Install SSL Certificate (Let's Encrypt)

### 4.1 Install Certbot for Apache

```bash
sudo apt install certbot python3-certbot-apache -y
```

### 4.2 Obtain Certificate

```bash
sudo certbot --apache -d yourdomain.com -d www.yourdomain.com
```

Follow prompts:
- Enter email address
- Agree to terms
- Choose redirect HTTP to HTTPS: **Yes (recommended)**

Certbot will automatically:
- Obtain SSL certificate
- Update Apache configuration
- Set up HTTPS redirect
- Configure auto-renewal

### 4.3 Verify SSL

Visit: https://www.ssllabs.com/ssltest/analyze.html?d=yourdomain.com

---

## Step 5: Final Apache Configuration (After SSL)

After Certbot configures SSL, your `/etc/apache2/sites-available/picker-le-ssl.conf` should look like:

```apache
<IfModule mod_ssl.c>
<VirtualHost *:443>
    ServerName yourdomain.com
    ServerAlias www.yourdomain.com
    ServerAdmin admin@yourdomain.com

    # SSL Configuration (managed by Certbot)
    SSLEngine on
    SSLCertificateFile /etc/letsencrypt/live/yourdomain.com/fullchain.pem
    SSLCertificateKeyFile /etc/letsencrypt/live/yourdomain.com/privkey.pem
    Include /etc/letsencrypt/options-ssl-apache.conf

    # Logging
    ErrorLog ${APACHE_LOG_DIR}/picker_ssl_error.log
    CustomLog ${APACHE_LOG_DIR}/picker_ssl_access.log combined

    # Static files
    Alias /static /var/www/picker/staticfiles
    <Directory /var/www/picker/staticfiles>
        Require all granted
        ExpiresActive On
        ExpiresDefault "access plus 1 month"
    </Directory>

    # Media files
    Alias /media /var/www/picker/media
    <Directory /var/www/picker/media>
        Require all granted
        ExpiresActive On
        ExpiresDefault "access plus 1 month"
    </Directory>

    # Proxy to Gunicorn
    ProxyPreserveHost On
    RequestHeader set X-Forwarded-Proto "https"
    RequestHeader set X-Forwarded-Port "443"

    ProxyPass /static !
    ProxyPass /media !
    ProxyPass / http://127.0.0.1:8000/
    ProxyPassReverse / http://127.0.0.1:8000/

    # Security headers
    Header always set Strict-Transport-Security "max-age=31536000; includeSubDomains"
    Header always set X-Frame-Options "DENY"
    Header always set X-Content-Type-Options "nosniff"
    Header always set X-XSS-Protection "1; mode=block"

    # Timeout settings (for long-running requests)
    ProxyTimeout 120
    TimeOut 120
</VirtualHost>
</IfModule>
```

---

## Step 6: Set Proper Permissions

```bash
# Static files directory
sudo chown -R picker:www-data /var/www/picker/staticfiles
sudo chmod -R 755 /var/www/picker/staticfiles

# Media files directory
sudo chown -R picker:www-data /var/www/picker/media
sudo chmod -R 755 /var/www/picker/media

# Application directory
sudo chown -R picker:picker /var/www/picker

# Logs directory
sudo chown -R picker:picker /var/www/picker/logs
sudo chmod -R 755 /var/www/picker/logs
```

---

## Step 7: Test Configuration

```bash
# Test Apache configuration
sudo apache2ctl configtest

# Test Django application
curl -I http://localhost:8000

# Test through Apache
curl -I http://yourdomain.com

# Test HTTPS
curl -I https://yourdomain.com

# Check if static files work
curl -I https://yourdomain.com/static/admin/css/base.css
```

---

## Firewall Configuration

```bash
# Allow Apache through firewall
sudo ufw allow 'Apache Full'

# Or manually
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Verify
sudo ufw status
```

---

## Troubleshooting

### Apache Won't Start

```bash
# Check Apache status
sudo systemctl status apache2

# Check for errors
sudo apache2ctl configtest

# View error log
sudo tail -f /var/log/apache2/error.log
```

### 502 Bad Gateway

```bash
# Check if Gunicorn is running
sudo systemctl status picker

# Check Gunicorn logs
sudo tail -f /var/www/picker/logs/gunicorn-error.log

# Test direct connection to Gunicorn
curl http://localhost:8000
```

### Static Files Not Loading

```bash
# Verify static files collected
ls -la /var/www/picker/staticfiles/

# Check permissions
ls -ld /var/www/picker/staticfiles/

# Recollect static files
cd /var/www/picker
source .venv/bin/activate
python manage.py collectstatic --noinput

# Check Apache config
sudo apache2ctl -S
```

### Permission Denied Errors

```bash
# Check SELinux (if enabled)
sudo setsebool -P httpd_can_network_connect 1

# Check file ownership
ls -la /var/www/picker/

# Fix ownership
sudo chown -R picker:www-data /var/www/picker/
```

---

## Apache Performance Tuning

### Enable MPM Event (Better Performance)

```bash
# Disable prefork
sudo a2dismod mpm_prefork

# Enable event MPM
sudo a2enmod mpm_event

# Restart Apache
sudo systemctl restart apache2
```

### Configure MPM Settings

```bash
sudo nano /etc/apache2/mods-available/mpm_event.conf
```

```apache
<IfModule mpm_event_module>
    StartServers             2
    MinSpareThreads         25
    MaxSpareThreads         75
    ThreadLimit             64
    ThreadsPerChild         25
    MaxRequestWorkers      150
    MaxConnectionsPerChild   0
</IfModule>
```

```bash
sudo systemctl restart apache2
```

---

## Enable Compression

```bash
# Enable mod_deflate
sudo a2enmod deflate

# Create compression config
sudo nano /etc/apache2/conf-available/compression.conf
```

```apache
<IfModule mod_deflate.c>
    AddOutputFilterByType DEFLATE text/html
    AddOutputFilterByType DEFLATE text/css
    AddOutputFilterByType DEFLATE text/javascript
    AddOutputFilterByType DEFLATE text/plain
    AddOutputFilterByType DEFLATE application/json
    AddOutputFilterByType DEFLATE application/javascript
    AddOutputFilterByType DEFLATE application/x-javascript
</IfModule>
```

```bash
sudo a2enconf compression
sudo systemctl restart apache2
```

---

## Monitoring Apache

### View Access Logs

```bash
# Real-time Apache access log
sudo tail -f /var/log/apache2/picker_access.log

# Real-time error log
sudo tail -f /var/log/apache2/picker_error.log
```

### Check Apache Status

```bash
# Enable mod_status
sudo a2enmod status

# Access at https://yourdomain.com/server-status (configure access first)
```

---

## Development vs Production Ports

### Development (Local Machine)

```bash
# Run Django directly on port 8080 if 8000 is taken
python manage.py runserver 8080

# Access at http://localhost:8080
```

### Production (With Apache)

```
- Django/Gunicorn: 127.0.0.1:8000 (internal only)
- Apache: 0.0.0.0:80 and 0.0.0.0:443 (public)
- Users access: https://yourdomain.com
```

---

## Apache Log Rotation

Logs are automatically rotated by logrotate:

```bash
# Check logrotate config
cat /etc/logrotate.d/apache2
```

If you need custom rotation:

```bash
sudo nano /etc/logrotate.d/picker
```

```
/var/log/apache2/picker*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 root adm
    sharedscripts
    postrotate
        if invoke-rc.d apache2 status > /dev/null 2>&1; then \
            invoke-rc.d apache2 reload > /dev/null 2>&1; \
        fi;
    endscript
}
```

---

## Update Application

```bash
cd /var/www/picker
source .venv/bin/activate

# Pull latest code
git pull origin main

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Restart Gunicorn
sudo systemctl restart picker

# Apache doesn't need restart (unless config changed)
```

---

## Security Hardening

### Hide Apache Version

```bash
sudo nano /etc/apache2/conf-available/security.conf
```

```apache
ServerTokens Prod
ServerSignature Off
```

```bash
sudo systemctl restart apache2
```

### Install ModSecurity (Web Application Firewall)

```bash
sudo apt install libapache2-mod-security2 -y
sudo a2enmod security2
sudo systemctl restart apache2
```

---

## Comparison: Apache vs Nginx

**Apache Advantages:**
- Already installed/familiar
- .htaccess support
- More modules available
- Better Windows support

**Nginx Advantages:**
- Better performance for static files
- Lower memory usage
- Better handling of concurrent connections
- Simpler configuration

**For Picker:** Both work well. Use what you're comfortable with!

---

## Additional Resources

- [Apache Documentation](https://httpd.apache.org/docs/2.4/)
- [ModSecurity](https://modsecurity.org/)
- [Apache Performance Tuning](https://httpd.apache.org/docs/2.4/misc/perf-tuning.html)
- [Let's Encrypt Apache Guide](https://certbot.eff.org/instructions?ws=apache)
