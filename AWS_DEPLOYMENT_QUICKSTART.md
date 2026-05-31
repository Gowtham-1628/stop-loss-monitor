# AWS Deployment Checklist - With Health Check

## Phase 1: AWS Console Setup ✅

### 1.1 Create EC2 Instance

- [ ] Go to AWS Console → EC2 → Launch Instance
- [ ] **Name**: `stop-loss-monitor`
- [ ] **AMI**: Ubuntu 22.04 LTS (free tier eligible)
- [ ] **Instance Type**: `t3.micro` (free tier)
- [ ] **Key Pair**: Create or select existing (download .pem file)
- [ ] **Storage**: 10 GB (default)
- [ ] Click **Launch**

### 1.2 Configure Security Group (Important!)

After instance is created:

- [ ] Go to **EC2** → **Instances**
- [ ] Select your instance
- [ ] Go to **Security** tab
- [ ] Click on security group link
- [ ] **Edit Inbound Rules**
- [ ] **Add rules:**

  **Rule 1 - SSH (already exists)**
  - Type: SSH
  - Port: 22
  - Source: Your IP or 0.0.0.0/0

  **Rule 2 - Health Check (NEW - IMPORTANT!)**
  - Type: Custom TCP
  - Port Range: 5000
  - Source: Your IP (e.g., 203.0.113.42/32) or 0.0.0.0/0
  - Description: Health Check Endpoint

- [ ] Click **Save rules**

### 1.3 Get Instance Details

- [ ] Note your **Public IPv4 Address** (e.g., 54.234.56.78)
- [ ] Keep your `.pem` key file safe

---

## Phase 2: SSH and Deploy 🚀

### 2.1 Connect to EC2

```bash
# On your local machine
chmod 400 /path/to/your-key.pem
ssh -i /path/to/your-key.pem ubuntu@YOUR_EC2_IP
```

### 2.2 Run Deployment Script

```bash
# On EC2 instance
cd /home/ubuntu

# Download and run deployment script
curl -O https://raw.githubusercontent.com/Gowtham-1628/stop-loss-monitor/main/deploy_to_ec2.sh
bash deploy_to_ec2.sh
```

Or manually:

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3.11 python3.11-venv python3-pip git curl

# Clone repository
mkdir -p /home/ubuntu/stop-loss-monitor && cd /home/ubuntu/stop-loss-monitor
git clone https://github.com/Gowtham-1628/stop-loss-monitor.git .

# Setup virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

### 2.3 Configure Environment

```bash
# Edit .env with your credentials
cp .env.example .env
nano .env
```

**Required values:**

```env
WEBULL_APP_KEY=your_key
WEBULL_APP_SECRET=your_secret
GOOGLE_SPREADSHEET_ID=your_sheet_id
TWILIO_ACCOUNT_SID=your_sid
TWILIO_AUTH_TOKEN=your_token
TWILIO_FROM_PHONE=+1234567890
TWILIO_TO_PHONE=+0987654321
```

### 2.4 Create Systemd Service

```bash
sudo tee /etc/systemd/system/stop-loss-monitor.service > /dev/null <<EOF
[Unit]
Description=Stop Loss Monitor
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/stop-loss-monitor
Environment="PATH=/home/ubuntu/stop-loss-monitor/venv/bin"
ExecStart=/home/ubuntu/stop-loss-monitor/venv/bin/python run_monitor.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable stop-loss-monitor
sudo systemctl start stop-loss-monitor
```

---

## Phase 3: Verification ✅

### 3.1 Check Service Status

```bash
# On EC2 instance
sudo systemctl status stop-loss-monitor

# Check logs
sudo journalctl -u stop-loss-monitor -f
```

### 3.2 Test Health Check Locally

```bash
# On EC2 instance
curl http://localhost:5000/health
curl http://localhost:5000/health/ready
curl http://localhost:5000/health/live
```

Expected response (200 OK):

```json
{
  "status": "healthy",
  "timestamp": "2026-05-31T10:30:45.123456",
  "uptime": 1234567.89,
  "version": "1.0.0"
}
```

### 3.3 Test Health Check from Local Machine

```bash
# On your local machine
curl http://YOUR_EC2_IP:5000/health
# Example: curl http://54.234.56.78:5000/health
```

---

## Phase 4: Monitor Operations 📊

### Useful Commands

```bash
# Check if monitor is running
sudo systemctl status stop-loss-monitor

# View recent logs
sudo journalctl -u stop-loss-monitor -n 50

# Follow logs in real-time
sudo journalctl -u stop-loss-monitor -f

# Restart service
sudo systemctl restart stop-loss-monitor

# Stop service
sudo systemctl stop stop-loss-monitor

# View application logs
tail -f /home/ubuntu/stop-loss-monitor/logs/*.log

# Check health status
curl http://localhost:5000/health/detailed
```

---

## Phase 5: Troubleshooting 🔧

### Health Check Not Responding

**Problem**: `curl http://EC2_IP:5000/health` times out

**Solutions**:

1. Check security group allows port 5000

   ```bash
   # AWS Console → Security Groups → Edit Inbound Rules
   # Verify Custom TCP 5000 is present
   ```

2. Check service is running

   ```bash
   sudo systemctl status stop-loss-monitor
   ```

3. Check port is listening

   ```bash
   sudo ss -tlnp | grep 5000
   ```

4. Check logs
   ```bash
   sudo journalctl -u stop-loss-monitor -n 100
   ```

### Service Fails to Start

```bash
# Check for errors
sudo systemctl status stop-loss-monitor

# View detailed logs
sudo journalctl -u stop-loss-monitor -n 50

# Try running directly to see errors
cd /home/ubuntu/stop-loss-monitor
source venv/bin/activate
python run_monitor.py
```

### Configuration Issues

```bash
# Validate .env
cat /home/ubuntu/stop-loss-monitor/.env

# Test config
python -c "from config import Config; Config.print_config()"
```

---

## Summary Checklist

- [ ] EC2 instance created and running
- [ ] Security group allows port 22 (SSH)
- [ ] Security group allows port 5000 (Health Check)
- [ ] Repository cloned from GitHub
- [ ] Python virtual environment created
- [ ] Dependencies installed (pip install -r requirements.txt)
- [ ] .env file configured with credentials
- [ ] Systemd service created and enabled
- [ ] Service starts successfully (sudo systemctl start stop-loss-monitor)
- [ ] Health check endpoint responds (curl http://localhost:5000/health)
- [ ] Can access health check from local machine (curl http://EC2_IP:5000/health)
- [ ] Logs are being written to logs/ directory
- [ ] Monitor is checking positions during market hours

---

## Useful Links

- [AWS Health Check Configuration](docs/AWS_HEALTH_CHECK.md) - Load balancer setup, alarms, monitoring
- [Health Check Endpoints](HEALTH_CHECK_QUICKSTART.md) - API endpoint reference
- [AWS Deployment Complete Guide](docs/AWS_DEPLOYMENT_COMPLETE.md) - Comprehensive setup guide

---

## Cost Estimate

- **EC2 t3.micro**: $0.0104/hour = ~$7.50/month (free tier eligible)
- **Data transfer**: Minimal (APIs only)
- **Total**: ~$7.50/month during free tier, then varies

Great for development and small-scale production!
