# 🚀 Deployment Guide

## Production Deployment

### Prerequisites

- Python 3.10 or higher
- OpenAI API account with Agent SDK access
- Gmail account with App Password configured
- Server with at least 1GB RAM
- Public URL (optional, for sharing)

---

## Quick Deploy

### 1. Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.10+
sudo apt install python3.10 python3-pip -y

# Install Git
sudo apt install git -y
```

### 2. Clone Repository

```bash
git clone https://github.com/robin-ochieng/openai-sdk-multi-agentic-workflow.git
cd openai-sdk-multi-agentic-workflow
git checkout deep-research-agent
```

### 3. Install Dependencies

```bash
# Install all requirements
pip install -r deep_research/requirements.txt

# Or install manually
pip install openai pydantic gradio python-dotenv
```

### 4. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit with your credentials
nano .env
```

Required variables:
```env
OPENAI_API_KEY=sk-proj-your_key_here
GMAIL_EMAIL=your_email@gmail.com
GMAIL_APP_PASSWORD=your_app_password_here
RECIPIENT_EMAIL=recipient@email.com
OPENAI_MODEL=gpt-4o-mini
```

### 5. Test Locally

```bash
# Run the application
python deep_research/app.py
```

Should output:
```
🔬 Starting Deep Research Agent...
📊 Loading web interface...
Running on local URL:  http://127.0.0.1:7860
```

Visit `http://localhost:7860` to test.

---

## Production Deployment Options

### Option 1: Direct Server Deployment

#### Using systemd (Ubuntu/Debian)

**1. Create service file:**

```bash
sudo nano /etc/systemd/system/deep-research.service
```

**Content:**
```ini
[Unit]
Description=Deep Research Agent
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/openai-sdk-multi-agentic-workflow
Environment="PATH=/usr/bin:/usr/local/bin"
ExecStart=/usr/bin/python3 deep_research/app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**2. Enable and start:**

```bash
sudo systemctl daemon-reload
sudo systemctl enable deep-research
sudo systemctl start deep-research
sudo systemctl status deep-research
```

**3. View logs:**

```bash
sudo journalctl -u deep-research -f
```

#### Using Nginx Reverse Proxy

**1. Install Nginx:**

```bash
sudo apt install nginx -y
```

**2. Configure Nginx:**

```bash
sudo nano /etc/nginx/sites-available/deep-research
```

**Content:**
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:7860;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

**3. Enable and restart:**

```bash
sudo ln -s /etc/nginx/sites-available/deep-research /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

**4. Add SSL (optional):**

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your-domain.com
```

---

### Option 2: Docker Deployment

**1. Create Dockerfile:**

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY deep_research/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose Gradio port
EXPOSE 7860

# Run application
CMD ["python", "deep_research/app.py"]
```

**2. Create docker-compose.yml:**

```yaml
version: '3.8'

services:
  deep-research:
    build: .
    ports:
      - "7860:7860"
    env_file:
      - .env
    restart: unless-stopped
    volumes:
      - ./deep_research/reports:/app/deep_research/reports
```

**3. Deploy:**

```bash
docker-compose up -d
docker-compose logs -f
```

---

### Option 3: Cloud Platform Deployment

#### Hugging Face Spaces

**1. Create Space:**
- Go to https://huggingface.co/spaces
- Create new Space (Gradio)
- Clone the Space repository

**2. Add files:**

```bash
git clone https://huggingface.co/spaces/your-username/deep-research
cd deep-research

# Copy deep_research package
cp -r /path/to/deep_research .

# Create app.py
cat > app.py << EOF
from deep_research.ui import launch_ui
launch_ui(share=True)
EOF

# Create requirements.txt
cat > requirements.txt << EOF
openai>=1.109.0
pydantic>=2.0.0
gradio>=4.0.0
python-dotenv>=1.0.0
EOF
```

**3. Add secrets:**
- Go to Space settings
- Add secrets: `OPENAI_API_KEY`, `GMAIL_EMAIL`, etc.

**4. Push:**

```bash
git add .
git commit -m "Deploy deep research agent"
git push
```

#### Railway.app

**1. Install Railway CLI:**

```bash
npm install -g @railway/cli
```

**2. Deploy:**

```bash
railway login
railway init
railway up
```

**3. Add environment variables** in Railway dashboard.

#### Render.com

**1. Create `render.yaml`:**

```yaml
services:
  - type: web
    name: deep-research
    env: python
    buildCommand: pip install -r deep_research/requirements.txt
    startCommand: python deep_research/app.py
    envVars:
      - key: OPENAI_API_KEY
        sync: false
      - key: GMAIL_EMAIL
        sync: false
      - key: GMAIL_APP_PASSWORD
        sync: false
      - key: RECIPIENT_EMAIL
        sync: false
```

**2. Connect GitHub** and deploy.

---

## Environment Configuration

### Production Environment Variables

```env
# API Keys
OPENAI_API_KEY=sk-proj-production_key

# Email Configuration
GMAIL_EMAIL=production@gmail.com
GMAIL_APP_PASSWORD=production_password
RECIPIENT_EMAIL=reports@company.com

# Model Configuration
OPENAI_MODEL=gpt-4o  # Use GPT-4 for production quality

# Environment
ENVIRONMENT=production

# Optional: Logging
LOG_LEVEL=INFO
```

### Security Best Practices

**1. Never commit `.env` file:**

```bash
# Add to .gitignore
echo ".env" >> .gitignore
```

**2. Use secrets management:**

- AWS Secrets Manager
- HashiCorp Vault
- Environment variables in hosting platform

**3. Rotate credentials regularly:**

- Generate new Gmail App Password monthly
- Rotate OpenAI API keys quarterly

---

## Scaling

### Horizontal Scaling

**Load Balancer Setup:**

```nginx
upstream deep_research {
    server 127.0.0.1:7860;
    server 127.0.0.1:7861;
    server 127.0.0.1:7862;
}

server {
    location / {
        proxy_pass http://deep_research;
    }
}
```

**Run multiple instances:**

```bash
# Instance 1
PORT=7860 python deep_research/app.py &

# Instance 2
PORT=7861 python deep_research/app.py &

# Instance 3
PORT=7862 python deep_research/app.py &
```

### Vertical Scaling

**Recommended Resources:**

| Users | CPU | RAM | Storage |
|-------|-----|-----|---------|
| 1-10 | 1 core | 1GB | 5GB |
| 10-50 | 2 cores | 2GB | 10GB |
| 50-100 | 4 cores | 4GB | 20GB |

### Performance Optimization

**1. Use GPT-4o-mini for speed:**

```python
manager = ResearchManager(model="gpt-4o-mini")
```

**2. Reduce search count:**

```python
# In planner_agent.py
HOW_MANY_SEARCHES = 3  # Instead of 5
```

**3. Enable caching:**

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def cached_search(query):
    return perform_search(query)
```

---

## Monitoring

### Health Check Endpoint

Add to `gradio_app.py`:

```python
@app.route("/health")
def health_check():
    return {"status": "healthy", "timestamp": datetime.now()}
```

### Logging

**Setup logging:**

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('deep_research.log'),
        logging.StreamHandler()
    ]
)
```

### Metrics

**Track key metrics:**

- Requests per minute
- Average response time
- Error rate
- Token usage
- Email success rate

**Example with Prometheus:**

```python
from prometheus_client import Counter, Histogram

requests_total = Counter('requests_total', 'Total requests')
response_time = Histogram('response_time', 'Response time')
```

---

## Backup & Recovery

### Database Backup

No database required - stateless application.

### Report Backup

```bash
# Backup reports directory
rsync -av deep_research/reports/ /backup/reports/

# Or use cron
0 2 * * * rsync -av /app/deep_research/reports/ /backup/reports/
```

### Configuration Backup

```bash
# Backup .env
cp .env .env.backup.$(date +%Y%m%d)
```

---

## Troubleshooting Production

### Common Issues

**Issue: Port already in use**

```bash
# Find process using port 7860
lsof -i :7860

# Kill process
kill -9 <PID>
```

**Issue: Out of memory**

```bash
# Check memory usage
free -h

# Restart service
sudo systemctl restart deep-research
```

**Issue: OpenAI rate limits**

- Upgrade OpenAI plan
- Implement request queuing
- Add retry logic with exponential backoff

**Issue: Email delivery failures**

- Check Gmail App Password
- Verify SMTP settings
- Review guardrails logs
- Check rate limiting

### Debug Mode

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Run with verbose output
DEBUG=true python deep_research/app.py
```

---

## Cost Estimation

### OpenAI API Costs (gpt-4o-mini)

| Component | Tokens | Cost/1M | Per Query |
|-----------|--------|---------|-----------|
| Planner | ~1,000 | $0.15 | $0.00015 |
| Search (×5) | ~10,000 | $0.15 | $0.0015 |
| Writer | ~5,000 | $0.60 | $0.003 |
| Email | ~2,000 | $0.15 | $0.0003 |
| **Total** | **~18,000** | - | **~$0.005** |

**Monthly estimate (1000 queries):** ~$5

### Gmail SMTP Costs

Free with Gmail account (up to 500 emails/day).

### Hosting Costs

| Platform | Cost/month |
|----------|-----------|
| Self-hosted VPS | $5-20 |
| Hugging Face Spaces | Free (community) |
| Railway.app | $5-10 |
| Render.com | $7+ |

---

## Maintenance

### Regular Tasks

**Daily:**
- Monitor error logs
- Check email delivery rate
- Review trace URLs for failures

**Weekly:**
- Review token usage
- Check disk space
- Update dependencies if needed

**Monthly:**
- Rotate credentials
- Review costs
- Backup reports

### Updates

```bash
# Pull latest changes
git pull origin deep-research-agent

# Update dependencies
pip install --upgrade -r deep_research/requirements.txt

# Restart service
sudo systemctl restart deep-research
```

---

## Security Hardening

### Firewall

```bash
# Allow only necessary ports
sudo ufw allow 22    # SSH
sudo ufw allow 80    # HTTP
sudo ufw allow 443   # HTTPS
sudo ufw enable
```

### Rate Limiting

Add to Nginx config:

```nginx
limit_req_zone $binary_remote_addr zone=research:10m rate=10r/m;

location / {
    limit_req zone=research burst=5;
    proxy_pass http://127.0.0.1:7860;
}
```

### HTTPS Only

```nginx
# Redirect HTTP to HTTPS
server {
    listen 80;
    return 301 https://$host$request_uri;
}
```

---

## Support

For issues or questions:
- Check [README.md](./README.md)
- Review [ARCHITECTURE.md](./ARCHITECTURE.md)
- See [API_REFERENCE.md](./API_REFERENCE.md)
- Check GitHub Issues

---

**Production deployment is complete when:**
✅ Application accessible via public URL
✅ All environment variables configured
✅ HTTPS enabled
✅ Monitoring in place
✅ Backups configured
✅ Documentation updated
