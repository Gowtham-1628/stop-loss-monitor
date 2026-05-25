# Manual EC2 Deployment Checklist

Follow these steps to deploy the Stop Loss Monitor manually to AWS EC2.

## Prerequisites

- AWS account with EC2 access
- EC2 key pair (.pem file)
- Webull API credentials
- Google Sheets ID with position data
- Twilio WhatsApp credentials
- Your local machine with the project code

---

## STEP 1: Create EC2 Instance (5 minutes)

1. Go to [AWS Console](https://console.aws.amazon.com/)
2. Navigate to **EC2** → **Instances** → **Launch Instance**
3. Configure:
   - **Name**: `stop-loss-monitor`
   - **AMI**: Ubuntu 22.04 LTS (free tier eligible)
   - **Instance Type**: `t3.micro`
   - **Key Pair**: Select or create one (download `.pem` file if new)
   - **Security Group**: Create new with:
     - Inbound: SSH (port 22) from your IP
     - Outbound: All traffic (required for API calls)
   - **Storage**: 10 GB (default fine)
4. Click **Launch** and wait for running status
5. **Copy the Public IPv4 address** (e.g., `54.234.56.78`)

---

## STEP 2: Connect to EC2 (2 minutes)

**On your local machine:**

```bash
# Make key file readable only by you
chmod 400 /path/to/your-key.pem

# SSH into EC2
ssh -i /path/to/your-key.pem ubuntu@YOUR_EC2_IP

# Example:
# ssh -i ~/.ssh/my-key.pem ubuntu@54.234.56.78
```

---

## STEP 3: Update System (3 minutes)

**On EC2 instance:**

```bash
sudo apt update && sudo apt upgrade -y
```

---

## STEP 4: Install Dependencies (5 minutes)

```bash
sudo apt install -y python3.11 python3-pip python3-venv git curl
```

---

## STEP 5: Deploy Project Code (5 minutes)

### Option A: Clone from GitHub (Easiest)

```bash
cd /home/ubuntu
git clone https://github.com/Gowtham-1628/stop-loss-monitor.git
cd stop-loss-monitor
```

### Option B: Copy from Local Machine (Faster if you have it)

**On your local machine (in a new terminal, NOT on EC2):**

```bash
cd "/Users/sai/Documents/Github 2/stop-loss-monitor"
scp -i /path/to/your-key.pem -r . ubuntu@YOUR_EC2_IP:/home/ubuntu/stop-loss-monitor/
```

**Then on EC2:**

```bash
cd /home/ubuntu/stop-loss-monitor
```

---

## STEP 6: Configure Environment (5 minutes)

```bash
# Copy the template
cp .env.example .env

# Edit with your credentials
nano .env
```

**Add these values:**

```env
WEBULL_APP_KEY=your_webull_app_key
WEBULL_APP_SECRET=your_webull_app_secret

GOOGLE_SPREADSHEET_ID=your_google_sheet_id

TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token
TWILIO_FROM_PHONE=+14155238886
TWILIO_TO_PHONE=+14846810612

MARKET_OPEN_TIME=09:30
MARKET_CLOSE_TIME=16:00
MARKET_TIMEZONE=America/New_York
CHECK_INTERVAL_MINUTES=5
ALERT_COOLDOWN_MINUTES=30
LOG_LEVEL=INFO
```

**Save**: Press `Ctrl+O` → `Enter` → `Ctrl+X`

Verify it saved:

```bash
cat .env
```

---

## STEP 7: Setup Python Virtual Environment (3 minutes)

```bash
python3 -m venv venv
source venv/bin/activate
```

---

## STEP 8: Install Python Dependencies (3 minutes)

```bash
pip install -r requirements.txt
```

Verify installation:

```bash
python -c "from modules.alert_manager import AlertManager; print('✓ All imports working')"
```

---

## STEP 9: Test the Application (5 minutes)

Test a single check cycle:

```bash
python -c "
from modules.alert_manager import AlertManager
from config import Config

manager = AlertManager(spreadsheet_id=Config.GOOGLE_SPREADSHEET_ID)
results = manager.check_positions()
print('✓ Test complete - check logs for details')
"
```

Check the logs:

```bash
tail -30 logs/monitor_*.log
```

**Expected**: Should show positions checked with prices and stop-loss levels.

---

## STEP 10: Setup Systemd Service (Auto-Start) (5 minutes)

Create the service file:

```bash
sudo nano /etc/systemd/system/stop-loss-monitor.service
```

Paste this content:

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

**Save**: `Ctrl+O` → `Enter` → `Ctrl+X`

---

## STEP 11: Start the Service (2 minutes)

```bash
# Reload systemd configuration
sudo systemctl daemon-reload

# Enable auto-start on reboot
sudo systemctl enable stop-loss-monitor

# Start the service
sudo systemctl start stop-loss-monitor

# Check status (should show "active (running)")
sudo systemctl status stop-loss-monitor
```

Press `Q` to exit the status view.

---

## STEP 12: Verify Service is Running (2 minutes)

```bash
# View live logs (press Ctrl+C to stop)
sudo journalctl -u stop-loss-monitor -f

# Or view last 50 lines
sudo journalctl -u stop-loss-monitor -n 50

# Check if service auto-restarts on failure
sudo systemctl restart stop-loss-monitor
sleep 2
sudo systemctl status stop-loss-monitor
```

---

## ✅ Deployment Complete!

Your Stop Loss Monitor is now running on EC2 and will:

- Check positions every 5 minutes during market hours (9:30-16:00 EST, M-F)
- Send WhatsApp alerts when stop-loss is triggered
- Auto-restart if it crashes
- Auto-start after EC2 reboot

---

## Troubleshooting

### Service won't start

```bash
sudo systemctl status stop-loss-monitor
sudo journalctl -u stop-loss-monitor -e
```

### Check current logs

```bash
tail -50 logs/monitor_*.log
```

### Restart service manually

```bash
sudo systemctl restart stop-loss-monitor
```

### Stop service (if needed)

```bash
sudo systemctl stop stop-loss-monitor
```

### SSH back into EC2 later

```bash
ssh -i /path/to/your-key.pem ubuntu@YOUR_EC2_IP
```

---

## Monitoring Commands

Save these for regular monitoring:

```bash
# Check service status
sudo systemctl status stop-loss-monitor

# View last 30 lines of logs
sudo journalctl -u stop-loss-monitor -n 30

# Follow logs in real-time
sudo journalctl -u stop-loss-monitor -f

# View alert history
cat logs/alert_history.json

# Check disk usage
df -h

# Check EC2 is still running (from your local machine)
# Go to AWS Console → EC2 → Instances
```

---

## Cost Optimization

The t3.micro instance costs ~$6-15/month. To reduce costs:

1. **Stop instance when not trading**: Go to AWS Console → EC2 → Select instance → Instance State → Stop (data persists)
2. **Delete unused EBS snapshots**: Reduce storage costs
3. **Use AWS Free Tier**: New accounts get 12 months free on t3.micro

---

## Next Steps

- [ ] Monitor the service for the first day
- [ ] Test an alert during market hours
- [ ] Set up GitHub Actions deployment (optional, for easier updates)
- [ ] Create CloudWatch alarms for instance health
- [ ] Schedule regular credential rotations
