#!/bin/bash
# AWS Deployment Setup Script
# Run this script after SSHing into your EC2 instance
# Usage: bash deploy_to_ec2.sh

set -e  # Exit on error

echo "=========================================="
echo "Stop Loss Monitor - AWS EC2 Setup"
echo "=========================================="
echo ""

# Color codes for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Step 1: Update system
echo -e "${YELLOW}[1/8]${NC} Updating system packages..."
sudo apt update
sudo apt upgrade -y
echo -e "${GREEN}✓ System updated${NC}\n"

# Step 2: Install Python and dependencies
echo -e "${YELLOW}[2/8]${NC} Installing Python 3.11 and dependencies..."
sudo apt install -y python3.11 python3.11-venv python3-pip git curl
echo -e "${GREEN}✓ Dependencies installed${NC}\n"

# Step 3: Create project directory
echo -e "${YELLOW}[3/8]${NC} Creating project directory..."
mkdir -p /home/ubuntu/stop-loss-monitor
cd /home/ubuntu/stop-loss-monitor
echo -e "${GREEN}✓ Directory created${NC}\n"

# Step 4: Clone from GitHub
echo -e "${YELLOW}[4/8]${NC} Cloning from GitHub..."
if [ -d ".git" ]; then
    echo "Repository already exists, pulling latest..."
    git pull origin main
else
    git clone https://github.com/Gowtham-1628/stop-loss-monitor.git .
fi
echo -e "${GREEN}✓ Repository cloned${NC}\n"

# Step 5: Create virtual environment
echo -e "${YELLOW}[5/8]${NC} Creating Python virtual environment..."
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip
echo -e "${GREEN}✓ Virtual environment created${NC}\n"

# Step 6: Install requirements
echo -e "${YELLOW}[6/8]${NC} Installing Python packages..."
pip install -r requirements.txt
echo -e "${GREEN}✓ Requirements installed${NC}\n"

# Step 7: Copy .env file
echo -e "${YELLOW}[7/8]${NC} Checking environment file..."
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠ .env file not found${NC}"
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo ""
    echo "⚠️  IMPORTANT: Edit .env with your credentials:"
    echo "   nano .env"
    echo ""
    echo "Required credentials:"
    echo "  - WEBULL_APP_KEY"
    echo "  - WEBULL_APP_SECRET"
    echo "  - GOOGLE_SPREADSHEET_ID"
    echo "  - TWILIO_ACCOUNT_SID"
    echo "  - TWILIO_AUTH_TOKEN"
    echo "  - TWILIO_FROM_PHONE"
    echo "  - TWILIO_TO_PHONE"
else
    echo -e "${GREEN}✓ .env file exists${NC}"
fi
echo ""

# Step 8: Create systemd service
echo -e "${YELLOW}[8/8]${NC} Creating systemd service..."
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
echo -e "${GREEN}✓ Systemd service created${NC}\n"

echo ""
echo "=========================================="
echo "✅ Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo ""
echo "1️⃣  Configure environment variables:"
echo "   nano /home/ubuntu/stop-loss-monitor/.env"
echo ""
echo "2️⃣  Start the monitor:"
echo "   sudo systemctl start stop-loss-monitor"
echo ""
echo "3️⃣  Enable auto-start on reboot:"
echo "   sudo systemctl enable stop-loss-monitor"
echo ""
echo "4️⃣  Check status:"
echo "   sudo systemctl status stop-loss-monitor"
echo ""
echo "5️⃣  View logs:"
echo "   sudo journalctl -u stop-loss-monitor -f"
echo ""
echo "6️⃣  Test health check endpoint:"
echo "   curl http://localhost:5000/health"
echo ""
echo "7️⃣  Update AWS Security Group:"
echo "   - Allow inbound TCP on port 5000"
echo "   - See docs/AWS_HEALTH_CHECK.md for details"
echo ""
