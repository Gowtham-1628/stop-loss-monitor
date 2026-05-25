# AWS Deployment - Complete Step-by-Step Guide

## Overview

Your stop-loss monitor will run 24/7 on AWS EC2 t3.micro ($6-15/month), checking positions every 5 minutes during market hours (9:30-16:00 EST Mon-Fri) and sending WhatsApp alerts when stop-loss is triggered.

---

## PHASE 1: AWS Setup (AWS Console)

### 1.1 Create EC2 Instance

1. Go to **AWS Console** → **EC2** → **Instances** → **Launch Instance**
2. Configure:
   - **Name**: `stop-loss-monitor`
   - **AMI**: Ubuntu 22.04 LTS (free tier eligible)
   - **Instance Type**: `t3.micro`
   - **Key Pair**: Create new or select existing (download .pem file)
   - **Security Group**: Create with:
     - **Inbound**: SSH (port 22) from your IP
     - **Outbound**: All (needed for API calls)
   - **Storage**: 10 GB (default)
3. Click **Launch** and wait for instance to be running

### 1.2 Note Instance Details

- **Instance IP**: Copy the public IPv4 address (e.g., `54.234.56.78`)
- **Key File**: Save your `.pem` key file in a secure location

---

## PHASE 2: Connect and Setup (Terminal/SSH)

### 2.1 SSH into Instance

```bash
# Change permissions on key file (first time only)
chmod 400 /path/to/your-key.pem

# SSH into instance
ssh -i /path/to/your-key.pem ubuntu@YOUR_INSTANCE_IP
```

### 2.2 Update System

```bash
sudo apt update && sudo apt upgrade -y
```

### 2.3 Install Python & Dependencies

```bash
sudo apt install -y python3.11 python3-pip python3-venv git curl
```

### 2.4 Create Project Directory

```bash
mkdir -p /home/ubuntu/stop-loss-monitor
cd /home/ubuntu/stop-loss-monitor
```

---

## PHASE 3: Deploy Project Code

### 3.1 Option A: Copy Files via SCP (Recommended)

```bash
# On your LOCAL machine, run:
cd "/Users/sai/Documents/Github 2/stop-loss-monitor"

# Copy entire project
scp -i /path/to/your-key.pem -r . ubuntu@YOUR_INSTANCE_IP:/home/ubuntu/stop-loss-monitor/
```

### 3.2 Option B: Clone from GitHub

```bash
# On EC2 instance:
cd /home/ubuntu
git clone https://github.com/Gowtham-1628/stop-loss-monitor.git
cd stop-loss-monitor
```

### 3.3 Verify Files Copied

```bash
ls -la /home/ubuntu/stop-loss-monitor/
# Should show: config.py, monitor.py, modules/, .env, requirements.txt, etc.
```

---

## PHASE 4: Configure Environment

### 4.1 Edit .env on EC2

```bash
# SSH into instance (if not already connected)
ssh -i /path/to/your-key.pem ubuntu@YOUR_INSTANCE_IP

# Navigate to project
cd /home/ubuntu/stop-loss-monitor

# Edit .env with your credentials
nano .env
```

### 4.2 Paste Your Credentials

⚠️ **IMPORTANT**: Use the `.env.example` template and fill in your actual values. Never commit real credentials to git.

```bash
# Copy the template
cp .env.example .env

# Edit with your credentials
nano .env
```

**Required values:**

- `WEBULL_APP_KEY`: Your Webull API key
- `WEBULL_APP_SECRET`: Your Webull API secret
- `GOOGLE_SPREADSHEET_ID`: Your Google Sheets ID
- `TWILIO_ACCOUNT_SID`: Your Twilio account SID
- `TWILIO_AUTH_TOKEN`: Your Twilio auth token
- `TWILIO_FROM_PHONE`: Twilio WhatsApp number (with +1 prefix)
- `TWILIO_TO_PHONE`: Your phone number to receive alerts

**Save**: Ctrl+O → Enter → Ctrl+X

### 4.3 Verify .env

```bash
cat .env  # Should show all credentials
```

---

## PHASE 5: Install Python Dependencies

### 5.1 Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 5.2 Install Requirements

```bash
pip install -r requirements.txt
```

### 5.3 Test Installation

```bash
python -c "from modules.alert_manager import AlertManager; print('✓ All imports working')"
```

---

## PHASE 6: Test Before Production

### 6.1 Test Position Check (Dry Run)

```bash
python << 'EOF'
from modules.alert_manager import AlertManager
from config import Config

manager = AlertManager(spreadsheet_id=Config.GOOGLE_SPREADSHEET_ID)
results = manager.check_positions()
print("✓ Test complete - Check logs/monitor_*.log")
EOF
```

### 6.2 Check Logs

```bash
tail -30 logs/monitor_*.log
```

**Expected Output**: Should show all 10 positions checked with entry thresholds and weekly lows.

---

## PHASE 7: Setup Systemd Service (Auto-Start)

### 7.1 Copy Service File

```bash
# Copy the systemd service file
sudo cp docs/stop-loss-monitor.service /etc/systemd/system/

# Or manually create:
sudo nano /etc/systemd/system/stop-loss-monitor.service
```

### 7.2 Paste Service Configuration

```ini
[Unit]
Description=Stop Loss Monitor - Real-time position monitoring
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/stop-loss-monitor
Environment="PATH=/home/ubuntu/stop-loss-monitor/venv/bin"
ExecStart=/home/ubuntu/stop-loss-monitor/venv/bin/python monitor.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

**Save**: Ctrl+O → Enter → Ctrl+X

### 7.3 Enable and Start Service

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable auto-start on reboot
sudo systemctl enable stop-loss-monitor

# Start the service
sudo systemctl start stop-loss-monitor

# Check status
sudo systemctl status stop-loss-monitor
```

**Expected**: Should show `active (running)`

### 7.4 View Live Logs

```bash
# Follow logs in real-time
sudo journalctl -u stop-loss-monitor -f

# Or view last 50 lines
sudo journalctl -u stop-loss-monitor -n 50
```

---

## PHASE 8: Monitoring & Maintenance

### 8.1 Daily Checks

```bash
# Check service is running
sudo systemctl status stop-loss-monitor

# View recent logs
sudo journalctl -u stop-loss-monitor --since "2 hours ago"
```

### 8.2 Manual Commands

```bash
# Stop service (if needed)
sudo systemctl stop stop-loss-monitor

# Restart service
sudo systemctl restart stop-loss-monitor

# Check service logs with timestamps
sudo journalctl -u stop-loss-monitor -S "2 hours ago" -n 100
```

### 8.3 Troubleshooting

```bash
# If service won't start, check for errors:
sudo systemctl status stop-loss-monitor

# View full log output:
sudo journalctl -u stop-loss-monitor -e

# SSH into instance and test manually:
ssh -i /path/to/key.pem ubuntu@YOUR_INSTANCE_IP
cd /home/ubuntu/stop-loss-monitor
source venv/bin/activate
python monitor.py  # Press Ctrl+C to stop
```

---

## PHASE 9: Cost Optimization (Optional)

### 9.1 Stop Instance When Not Needed

```bash
# Stop (don't terminate) to preserve all data
# In AWS Console: EC2 → Instances → Select instance → Instance State → Stop

# Restart later
# In AWS Console: EC2 → Instances → Select instance → Instance State → Start
```

### 9.2 Set Up Billing Alerts

- AWS Console → Billing → Budgets → Create Budget
- Set limit: $20/month (gives buffer for t3.micro at ~$10/month)

---

## PHASE 10: Verification Checklist

✅ **Before Production, Verify:**

- [ ] EC2 instance is running (green status in AWS Console)
- [ ] Can SSH into instance
- [ ] All .env credentials are correct
- [ ] Virtual environment created and activated
- [ ] Dependencies installed (`pip list` shows all packages)
- [ ] Test position check ran successfully
- [ ] Systemd service is enabled and running
- [ ] `sudo journalctl -u stop-loss-monitor` shows recent logs
- [ ] WhatsApp credentials working (previous tests showed success)

---

## PHASE 11: Production Deployment

### 11.1 Start Monitoring

```bash
# Service is already running from Step 7.3
# Monitor logs in real-time:
ssh -i /path/to/key.pem ubuntu@YOUR_INSTANCE_IP
sudo journalctl -u stop-loss-monitor -f
```

### 11.2 Expected Behavior

- Every 5 minutes during market hours (9:30-16:00 EST):
  - Fetches 10 positions from Google Sheet
  - Gets current prices and previous week lows
  - Compares: current price vs min(0.9×entry_price, weekly_low)
  - Sends WhatsApp alert if stop-loss triggered
  - Logs all details with timestamps
- After 4 PM EST: Service sleeps (cost optimization)
- Each position gets 30-min alert cooldown (prevents duplicate alerts)

### 11.3 Monitor Performance

```bash
# Check memory usage:
free -h

# Check disk usage:
df -h

# View logs with grep:
sudo journalctl -u stop-loss-monitor | grep "STOP LOSS"
```

---

## Quick Reference

| Task              | Command                                    |
| ----------------- | ------------------------------------------ |
| SSH into instance | `ssh -i key.pem ubuntu@IP_ADDRESS`         |
| Start service     | `sudo systemctl start stop-loss-monitor`   |
| Stop service      | `sudo systemctl stop stop-loss-monitor`    |
| View logs         | `sudo journalctl -u stop-loss-monitor -f`  |
| Check status      | `sudo systemctl status stop-loss-monitor`  |
| Restart service   | `sudo systemctl restart stop-loss-monitor` |
| Stop EC2 instance | AWS Console → Instance State → Stop        |

---

## Support & Debugging

**If service won't start:**

1. SSH into instance
2. Activate venv: `source venv/bin/activate`
3. Run manually: `python monitor.py`
4. Check for errors in output
5. Fix .env or dependencies as needed
6. Restart: `sudo systemctl restart stop-loss-monitor`

**If WhatsApp alerts not sending:**

1. Check Twilio credentials in .env
2. Test manually:
   ```bash
   python -c "from modules.whatsapp_notifier import WhatsAppNotifier; n = WhatsAppNotifier(); n.send_test_message()"
   ```
3. Check AWS security group allows outbound HTTPS

**If positions not being fetched:**

1. Check Google Sheet is public and accessible
2. Test manually:
   ```bash
   python -c "from modules.position_reader import PositionReader; from config import Config; p = PositionReader(Config.GOOGLE_SPREADSHEET_ID); print(p.get_symbols())"
   ```

---

## Estimated Timeline

- **AWS Setup**: 5 minutes
- **SSH & System Setup**: 5 minutes
- **Code Deployment**: 5 minutes (via SCP)
- **Environment Config**: 2 minutes
- **Dependency Install**: 3 minutes
- **Testing**: 5 minutes
- **Systemd Setup**: 2 minutes
- **Total**: ~25 minutes to production

**Estimated Monthly Cost**: $10-15 (t3.micro at ~$0.0104/hour)

---

Good luck with deployment! 🚀
