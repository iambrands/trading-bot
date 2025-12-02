# Crypto Scalping Trading Bot - Deployment Guide

Complete guide for deploying Crypto Scalping Trading Bot to production environments (AWS, GCP, or local server).

## Prerequisites

- Python 3.8 or higher
- PostgreSQL 12+ database
- Coinbase Advanced Trade API credentials
- Server with stable internet connection
- Domain name (optional, for external API access)

## Deployment Options

### Option 1: Local Server / VPS

#### Step 1: Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and pip
sudo apt install python3 python3-pip python3-venv -y

# Install PostgreSQL
sudo apt install postgresql postgresql-contrib -y

# Install git
sudo apt install git -y
```

#### Step 2: Database Setup

```bash
# Switch to postgres user
sudo -u postgres psql

# Create database and user
CREATE DATABASE tradingbot;
CREATE USER tradingbot_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE tradingbot TO tradingbot_user;
\q
```

#### Step 3: Application Deployment

```bash
# Clone repository
cd /opt
sudo git clone <repository-url> tradingbot
sudo chown -R $USER:$USER tradingbot
cd tradingbot

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
nano .env  # Edit with your configuration
```

#### Step 4: Systemd Service

Create `/etc/systemd/system/tradingbot.service`:

```ini
[Unit]
Description=Crypto Scalping Trading Bot
After=network.target postgresql.service

[Service]
Type=simple
User=your_username
WorkingDirectory=/opt/tradingbot
Environment="PATH=/opt/tradingbot/venv/bin"
ExecStart=/opt/tradingbot/venv/bin/python /opt/tradingbot/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable tradingbot
sudo systemctl start tradingbot
sudo systemctl status tradingbot
```

### Option 2: AWS EC2 Deployment

#### Step 1: Launch EC2 Instance

1. Launch EC2 instance (Ubuntu 22.04 LTS recommended)
2. Security Group: Open port 8000 (API) and 22 (SSH)
3. Configure key pair for SSH access

#### Step 2: Setup RDS PostgreSQL

1. Create RDS PostgreSQL instance
2. Configure security group to allow EC2 access
3. Note connection details (endpoint, port, credentials)

#### Step 3: Deploy Application

SSH into EC2 instance and follow Local Server steps, using RDS endpoint for database.

### Option 3: Docker Deployment

#### Step 1: Create Dockerfile

Create `Dockerfile`:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Run application
CMD ["python", "main.py"]
```

#### Step 2: Create docker-compose.yml

```yaml
version: '3.8'

services:
  db:
    image: postgres:14
    environment:
      POSTGRES_DB: tradingbot
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: your_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  tradingbot:
    build: .
    environment:
      - ENVIRONMENT=production
      - DB_HOST=db
      - DB_PORT=5432
      - DB_NAME=tradingbot
      - DB_USER=postgres
      - DB_PASSWORD=your_password
      - PAPER_TRADING=false
    depends_on:
      - db
    ports:
      - "8000:8000"
    volumes:
      - ./logs:/app/logs

volumes:
  postgres_data:
```

#### Step 3: Deploy

```bash
docker-compose up -d
docker-compose logs -f tradingbot
```

### Option 4: Google Cloud Platform (GCP)

#### Step 1: Setup Cloud SQL

1. Create Cloud SQL PostgreSQL instance
2. Create database: `tradingbot`
3. Create user with appropriate permissions

#### Step 2: Deploy to Compute Engine

1. Create VM instance (Ubuntu 22.04)
2. Install dependencies (see Local Server steps)
3. Deploy application
4. Configure firewall rules for port 8000

## Environment Configuration

### Production .env Template

```env
ENVIRONMENT=production

# Coinbase API Credentials
COINBASE_API_KEY=your_production_api_key
COINBASE_API_SECRET=your_production_api_secret
COINBASE_API_PASSPHRASE=your_production_passphrase

# Database Settings
DB_HOST=your_db_host
DB_PORT=5432
DB_NAME=tradingbot
DB_USER=tradingbot_user
DB_PASSWORD=your_secure_password

# Trading Mode
PAPER_TRADING=false

# Alert Settings
SLACK_WEBHOOK_URL=your_slack_webhook
TELEGRAM_BOT_TOKEN=your_telegram_token
TELEGRAM_CHAT_ID=your_telegram_chat_id

# Logging
LOG_LEVEL=WARNING
```

## Security Best Practices

### 1. Secure API Keys

- Never commit `.env` file to version control
- Use environment variables or secrets manager (AWS Secrets Manager, GCP Secret Manager)
- Rotate API keys regularly
- Use read-only API keys if possible

### 2. Database Security

- Use strong database passwords
- Restrict database access to application server only
- Enable SSL/TLS for database connections
- Regular database backups

### 3. Network Security

- Use firewall rules to restrict API access
- Implement reverse proxy (nginx) with SSL/TLS
- Use VPN or SSH tunnel for administration
- Rate limit API endpoints

### 4. Application Security

- Run bot as non-root user
- Implement proper logging and monitoring
- Regular security updates
- Monitor for suspicious activity

## Nginx Reverse Proxy Setup

Install nginx:

```bash
sudo apt install nginx -y
```

Create `/etc/nginx/sites-available/tradingbot`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable site:

```bash
sudo ln -s /etc/nginx/sites-available/tradingbot /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## SSL/TLS Setup (Let's Encrypt)

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your-domain.com
```

## Monitoring Setup

### 1. Log Monitoring

Monitor logs:

```bash
# Follow logs
tail -f /opt/tradingbot/tradingbot.log

# Check for errors
grep ERROR /opt/tradingbot/tradingbot.log

# Systemd journal
journalctl -u tradingbot -f
```

### 2. Process Monitoring

Install monitoring tools:

```bash
sudo apt install htop iotop -y
```

### 3. Database Monitoring

Monitor database:

```bash
# Connect to database
psql -U tradingbot_user -d tradingbot

# Check recent trades
SELECT * FROM trades ORDER BY entry_time DESC LIMIT 10;

# Check daily performance
SELECT * FROM performance_metrics ORDER BY date DESC LIMIT 7;
```

### 4. API Health Checks

Create health check script:

```bash
#!/bin/bash
# health_check.sh

curl -f http://localhost:8000/api/status || exit 1
```

Add to crontab:

```bash
*/5 * * * * /path/to/health_check.sh
```

## Backup Strategy

### Database Backups

```bash
# Create backup script
cat > /opt/tradingbot/backup_db.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/opt/tradingbot/backups"
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump -U tradingbot_user tradingbot > "$BACKUP_DIR/tradingbot_$DATE.sql"
# Keep only last 7 days
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
EOF

chmod +x /opt/tradingbot/backup_db.sh

# Daily backup via cron
0 2 * * * /opt/tradingbot/backup_db.sh
```

### Log Rotation

Configure logrotate `/etc/logrotate.d/tradingbot`:

```
/opt/tradingbot/tradingbot.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
}
```

## Performance Optimization

### 1. Database Optimization

```sql
-- Create indexes (already in code, but verify)
CREATE INDEX IF NOT EXISTS idx_trades_pair ON trades(pair);
CREATE INDEX IF NOT EXISTS idx_trades_entry_time ON trades(entry_time);

-- Analyze tables
ANALYZE trades;
ANALYZE performance_metrics;
```

### 2. Connection Pooling

Database connection pooling is already configured in `db_manager.py` (min_size=2, max_size=10). Adjust based on load.

### 3. Resource Limits

Monitor CPU and memory usage. Adjust loop intervals if needed:

```python
# In config.py
LOOP_INTERVAL_SECONDS = 3  # Faster in production
```

## Troubleshooting Production Issues

### Bot Not Starting

1. Check logs: `journalctl -u tradingbot -n 50`
2. Verify database connection
3. Check API credentials
4. Verify file permissions

### Database Connection Errors

1. Verify database is running: `sudo systemctl status postgresql`
2. Check connection settings in `.env`
3. Test connection: `psql -h localhost -U tradingbot_user -d tradingbot`
4. Check firewall rules

### API Not Responding

1. Check if bot is running: `sudo systemctl status tradingbot`
2. Test API directly: `curl http://localhost:8000/api/status`
3. Check port availability: `netstat -tulpn | grep 8000`
4. Review nginx configuration if using reverse proxy

### No Trades Executing

1. Check strategy signals in logs
2. Verify risk manager validation
3. Check account balance
4. Review market data connectivity

## Production Checklist

Before going live:

- [ ] Paper trading tested thoroughly
- [ ] All environment variables configured
- [ ] Database backed up and secured
- [ ] API keys secured (not in code)
- [ ] Monitoring and alerts configured
- [ ] Backup strategy implemented
- [ ] SSL/TLS configured
- [ ] Firewall rules configured
- [ ] Log rotation configured
- [ ] Health checks implemented
- [ ] Kill switch tested
- [ ] Daily loss limits verified
- [ ] Performance metrics baseline established
- [ ] Documentation reviewed
- [ ] Emergency procedures documented

## Scaling Considerations

### Horizontal Scaling

The bot is designed for single-instance deployment. For multiple instances:

1. Use separate database per instance
2. Implement distributed locking for positions
3. Coordinate kill switch across instances
4. Aggregate performance metrics

### Vertical Scaling

For higher performance:

1. Increase database connection pool size
2. Optimize database queries
3. Use faster database instance
4. Increase server resources (CPU, RAM)

## Maintenance

### Regular Tasks

- **Daily**: Review performance metrics and logs
- **Weekly**: Review trades and strategy performance
- **Monthly**: Database maintenance and optimization
- **Quarterly**: Security audit and key rotation

### Updates

1. Pull latest code changes
2. Test in paper trading mode
3. Review changelog
4. Backup database
5. Deploy updates during low-activity periods
6. Monitor closely after deployment

## Support and Resources

- Check logs: `/opt/tradingbot/tradingbot.log`
- API status: `GET /api/status`
- Database queries for detailed analysis
- Review monitoring dashboards

## Emergency Procedures

### Immediate Shutdown

```bash
# Via API
curl -X POST http://localhost:8000/api/kill-switch

# Via systemd
sudo systemctl stop tradingbot
```

### Data Recovery

```bash
# Restore database backup
psql -U tradingbot_user -d tradingbot < backup_file.sql
```

### Rollback Procedure

1. Stop current version
2. Restore previous code version
3. Restore database backup if needed
4. Restart service
5. Monitor closely

## Conclusion

This deployment guide provides comprehensive instructions for deploying Crypto Scalping Trading Bot in various environments. Always test thoroughly in paper trading mode before deploying to production with real funds.
