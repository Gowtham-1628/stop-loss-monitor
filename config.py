"""
Configuration management for Stop Loss Monitor
Loads settings from environment variables with defaults
"""
import os
from pathlib import Path
from dotenv import load_dotenv
import logging

# Load .env file
ENV_FILE = Path(__file__).parent / ".env"
if ENV_FILE.exists():
    load_dotenv(ENV_FILE)
else:
    print(f"⚠️  Warning: .env file not found at {ENV_FILE}")
    print("   Create one by copying from .env.example")

# ── Application Configuration ──────────────────────────────────
class Config:
    """Central configuration for Stop Loss Monitor"""
    
    # ── Webull API ──────────────────────────────────────────
    WEBULL_APP_KEY = os.getenv("WEBULL_APP_KEY", "")
    WEBULL_APP_SECRET = os.getenv("WEBULL_APP_SECRET", "")
    
    # ── Google Sheets ───────────────────────────────────────
    GOOGLE_SPREADSHEET_ID = os.getenv("GOOGLE_SPREADSHEET_ID", "")
    GOOGLE_SHEET_RANGE = "Sheet1!A:A"  # Read symbols from column A
    
    # ── Twilio WhatsApp ────────────────────────────────────
    TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
    TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
    TWILIO_FROM_PHONE = os.getenv("TWILIO_FROM_PHONE", "")
    TWILIO_TO_PHONE = os.getenv("TWILIO_TO_PHONE", "")
    
    # ── Market Hours (EST) ──────────────────────────────────
    MARKET_OPEN_TIME = os.getenv("MARKET_OPEN_TIME", "09:30")
    MARKET_CLOSE_TIME = os.getenv("MARKET_CLOSE_TIME", "16:00")
    MARKET_TIMEZONE = os.getenv("MARKET_TIMEZONE", "America/New_York")
    
    # ── Check Frequency & Cooldown ─────────────────────────
    CHECK_INTERVAL_MINUTES = int(os.getenv("CHECK_INTERVAL_MINUTES", "5"))
    ALERT_COOLDOWN_MINUTES = int(os.getenv("ALERT_COOLDOWN_MINUTES", "30"))
    
    # ── Logging Configuration ──────────────────────────────
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_DIR = Path(__file__).parent / "logs"
    LOG_DIR.mkdir(exist_ok=True)
    
    # ── Webull API Configuration ────────────────────────────
    WEBULL_HOST = "api.webull.com"
    WEBULL_TIMESPAN = "W"  # Weekly bars
    WEBULL_WEEKS_TO_FETCH = 52  # Last 52 weeks for weekly low
    
    @classmethod
    def validate(cls):
        """Validate required configuration is set"""
        errors = []
        
        required_fields = [
            ("WEBULL_APP_KEY", cls.WEBULL_APP_KEY),
            ("WEBULL_APP_SECRET", cls.WEBULL_APP_SECRET),
            ("GOOGLE_SPREADSHEET_ID", cls.GOOGLE_SPREADSHEET_ID),
            ("TWILIO_ACCOUNT_SID", cls.TWILIO_ACCOUNT_SID),
            ("TWILIO_AUTH_TOKEN", cls.TWILIO_AUTH_TOKEN),
            ("TWILIO_FROM_PHONE", cls.TWILIO_FROM_PHONE),
            ("TWILIO_TO_PHONE", cls.TWILIO_TO_PHONE),
        ]
        
        for field_name, field_value in required_fields:
            if not field_value:
                errors.append(f"Missing required config: {field_name}")
        
        if errors:
            print("❌ Configuration Errors:")
            for error in errors:
                print(f"   - {error}")
            return False
        
        return True
    
    @classmethod
    def print_config(cls):
        """Print non-sensitive configuration (for debugging)"""
        print("\n" + "=" * 60)
        print("Configuration Summary")
        print("=" * 60)
        print(f"Webull App Key:        {cls.WEBULL_APP_KEY[:8]}...{cls.WEBULL_APP_KEY[-4:]}")
        print(f"Google Sheet ID:       {cls.GOOGLE_SPREADSHEET_ID[:20]}...")
        print(f"Twilio Account:        {cls.TWILIO_ACCOUNT_SID[:8]}...")
        print(f"Market Hours:          {cls.MARKET_OPEN_TIME} - {cls.MARKET_CLOSE_TIME} {cls.MARKET_TIMEZONE}")
        print(f"Check Interval:        {cls.CHECK_INTERVAL_MINUTES} minutes")
        print(f"Alert Cooldown:        {cls.ALERT_COOLDOWN_MINUTES} minutes")
        print(f"Log Level:             {cls.LOG_LEVEL}")
        print("=" * 60 + "\n")


# Create logger
def get_logger(name):
    """Create configured logger"""
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        logger.setLevel(getattr(logging, Config.LOG_LEVEL))
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(getattr(logging, Config.LOG_LEVEL))
        formatter = logging.Formatter(
            '[%(asctime)s] [%(levelname)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # File handler
        log_file = Config.LOG_DIR / f"monitor_{Path.cwd().name}.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(getattr(logging, Config.LOG_LEVEL))
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger