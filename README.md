# Stop Loss Monitor 📈

Real-time stock position monitoring with automated stop-loss alerts. Tracks your portfolio positions and sends instant WhatsApp notifications when stop-loss levels are hit during market hours.

## Features ✨

- **Real-time Market Data**: Integrates with Webull API for live stock prices
- **Google Sheets Integration**: Read positions from a Google Sheets spreadsheet
- **Smart Stop-Loss Logic**: Validates against previous week's low price
- **WhatsApp Alerts**: Instant notifications via Twilio when stop-loss is triggered
- **Market Hours Only**: Runs checks only during NYSE trading hours (9:30 AM - 4:00 PM EST, M-F)
- **Alert Cooldown**: Prevents duplicate alerts within 30-minute windows
- **Comprehensive Logging**: Tracks all position checks and alerts
- **Automated Deployment**: GitHub Actions CI/CD to AWS EC2

## Quick Start

### Prerequisites

- Python 3.11+
- Google Sheets with position data
- Webull API credentials
- Twilio account with WhatsApp enabled
- AWS EC2 instance (optional, for production deployment)

### Local Development

1. **Clone and setup:**

```bash
git clone https://github.com/Gowtham-1628/stop-loss-monitor.git
cd stop-loss-monitor
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Configure environment:**

```bash
cp .env.example .env
# Edit .env with your credentials:
nano .env
```

3. **Run tests:**

```bash
python run_comprehensive_tests.py
```

4. **Start monitoring:**

```bash
python run_monitor.py
```

## Configuration

Create a `.env` file with the following variables:

```env
# Webull API
WEBULL_APP_KEY=your_key_here
WEBULL_APP_SECRET=your_secret_here

# Google Sheets
GOOGLE_SPREADSHEET_ID=your_sheet_id

# Twilio WhatsApp
TWILIO_ACCOUNT_SID=your_sid
TWILIO_AUTH_TOKEN=your_token
TWILIO_FROM_PHONE=+14155238886
TWILIO_TO_PHONE=+1234567890

# Market Configuration
MARKET_OPEN_TIME=09:30
MARKET_CLOSE_TIME=16:00
MARKET_TIMEZONE=America/New_York
CHECK_INTERVAL_MINUTES=5
ALERT_COOLDOWN_MINUTES=30
LOG_LEVEL=INFO
```

## Project Structure

```
stop-loss-monitor/
├── config.py                          # Configuration management
├── monitor.py                         # Main application
├── run_monitor.py                     # Entry point
├── requirements.txt                   # Python dependencies
├── modules/
│   ├── alert_manager.py               # Orchestrates position checks & alerts
│   ├── position_reader.py             # Reads positions from Google Sheets
│   ├── stop_loss_validator.py         # Validates stop-loss hits
│   ├── webull_market_data.py          # Fetches market data from Webull API
│   ├── whatsapp_notifier.py           # Sends WhatsApp alerts via Twilio
│   └── logger.py                      # Logging configuration
├── tests/                             # Unit and integration tests
├── logs/                              # Application logs
├── docs/
│   ├── AWS_DEPLOYMENT_COMPLETE.md     # AWS EC2 deployment guide
│   └── GITHUB_ACTIONS_DEPLOYMENT.md   # CI/CD setup guide
└── .github/workflows/
    └── deploy.yml                     # GitHub Actions workflow
```

## How It Works

1. **Position Reading**: Reads stock symbols and entry prices from Google Sheets
2. **Market Hours Check**: Only runs during NYSE trading hours (9:30-16:00 EST, M-F)
3. **Data Fetching**: Gets current price and previous week's low from Webull
4. **Validation**: Compares current price to stop-loss level (previous week's low)
5. **Alert Sending**: Sends WhatsApp notification if stop-loss is hit
6. **Cooldown**: Prevents duplicate alerts for 30 minutes
7. **Logging**: Records all checks and alerts for tracking

## Deployment

### Local Machine

```bash
python run_monitor.py
```

### AWS EC2 (Production)

Follow the [AWS Deployment Guide](docs/AWS_DEPLOYMENT_COMPLETE.md) for detailed instructions on:

- Creating an EC2 instance
- Installing dependencies
- Setting up systemd service for auto-start
- Monitoring in production

### Automated Deployment with GitHub Actions

Follow the [GitHub Actions Deployment Guide](docs/GITHUB_ACTIONS_DEPLOYMENT.md) for:

- Setting up GitHub Secrets
- Configuring EC2 for auto-deployment
- Testing the CI/CD pipeline

## Testing

Run the comprehensive test suite:

```bash
python run_comprehensive_tests.py
```

Or run specific tests:

```bash
python -m pytest tests/test_alert_manager.py -v
python -m pytest tests/test_integration.py -v
```

See [Testing Guide](tests/testing_guide.md) for detailed test information.

## Logs

Application logs are stored in `logs/` directory:

- `monitor_YYYY-MM-DD.log` - Main application logs
- `alert_history.json` - Record of all alerts sent

View recent logs:

```bash
tail -50 logs/monitor_*.log
```

## API Integrations

### Webull

- Fetches real-time stock prices
- Retrieves historical price data for weekly lows
- [Documentation](https://www.webull.com/api-intro)

### Google Sheets

- Reads position data (symbols, entry prices)
- Requires OAuth2 credentials

### Twilio

- Sends WhatsApp notifications
- Requires account with WhatsApp enabled

## Troubleshooting

**Issue**: Market data not updating

- Check Webull credentials in `.env`
- Verify API rate limits not exceeded

**Issue**: WhatsApp alerts not sending

- Verify Twilio credentials
- Check phone numbers in `.env` (must include country code)
- Ensure Twilio account has WhatsApp enabled

**Issue**: Google Sheets not reading positions

- Verify GOOGLE_SPREADSHEET_ID
- Check Google Sheets contains data in Column A
- Ensure OAuth credentials are current

**Issue**: Service not running on EC2

- Check service status: `sudo systemctl status stop-loss-monitor`
- View logs: `sudo journalctl -u stop-loss-monitor -f`

## Contributing

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Make changes and test: `python run_comprehensive_tests.py`
3. Commit: `git commit -am "Add your feature"`
4. Push: `git push origin feature/your-feature`
5. Create a Pull Request

## Security

- Never commit `.env` file or credentials (protected by .gitignore)
- Rotate API keys regularly
- Use environment variables for all secrets
- For production, use AWS IAM roles instead of hardcoded credentials

## License

MIT License - see LICENSE file for details

## Support

For issues and questions:

- Check [Troubleshooting](#troubleshooting) section
- Review deployment guides in `/docs`
- Check application logs in `/logs`

## Roadmap

- [ ] Email notifications as backup to WhatsApp
- [ ] Dashboard for portfolio visualization
- [ ] Historical alert tracking database
- [ ] Admin CLI for manual position checks
- [ ] CloudWatch metrics and alarms
- [ ] Support for multiple brokerage APIs
- [ ] Mobile app companion

---

**Status**: ✅ Actively maintained | **Last Updated**: May 2026
