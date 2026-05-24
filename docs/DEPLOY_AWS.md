# AWS Deployment Guide

## Prerequisites

- AWS account with EC2 access
- SSH key pair created in AWS
- Budget: ~$6-15/month for t3.micro instance

---

## Step 1: Launch EC2 Instance

1. Go to AWS Console → EC2 → Instances → Launch Instance
2. **Name**: `stop-loss-monitor`
3. **AMI**: Ubuntu 22.04 LTS (Free tier eligible)
4. **Instance type**: `t3.micro` (~$0.0104/hour)
5. **Key pair**: Create or select existing
6. **Security group**:
   - Allow SSH (port 22) from your IP
   - Allow outbound HTTPS (for API calls)
7. **Storage**: 10 GB (default)
8. **Launch**

---

## Step 2: Connect to Instance

```bash
# SSH into instance
ssh -i /path/to/key.pem ubuntu@your-instance-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install -y python3.11 python3-pip python3-venv git

# Create working directory
mkdir -p /home/ubuntu/stop-loss-monitor
cd /home/ubuntu/stop-loss-monitor
```

Step 3: Clone and Setup Project

# Clone or copy your project

git clone https://github.com/yourusername/stop-loss-monitor.git .

# Or manually copy files using SCP

# Create virtual environment

python3 -m venv venv
source venv/bin/activate

# Install dependencies

pip install -r requirements.txt

Step 4: Configure Environment

# Copy and edit .env

cp .env.example .env
nano .env # Edit with your credentials

# Upload Google credentials

# Option A: SCP from local

scp -i key.pem credentials.json ubuntu@instance:/home/ubuntu/stop-loss-monitor/

# Option B: Manually create (if small)

nano credentials.json # Paste contents

Step 5: Setup SystemD Service

sudo nano /etc/systemd/system/stop-loss-monitor.service

# Enable and start:

sudo systemctl daemon-reload
sudo systemctl enable stop-loss-monitor
sudo systemctl start stop-loss-monitor

# Check status

sudo systemctl status stop-loss-monitor

# View logs

sudo journalctl -u stop-loss-monitor -f # Follow logs

Step 6: Setup CloudWatch Logging (Optional)

# Install CloudWatch agent

wget https://s3.amazonaws.com/amazoncloudwatch-agent/ubuntu/amd64/latest/amazon-cloudwatch-agent.deb
sudo dpkg -i -E ./amazon-cloudwatch-agent.deb

# Configure (follow prompts)

sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-config-wizard
