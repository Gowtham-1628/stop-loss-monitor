"""
Centralized Logging System
Logs all monitoring activities, checks, and alerts
"""
from pathlib import Path
import logging
import time
from datetime import datetime
import pytz
from config import Config

class TimezoneFormatter(logging.Formatter):
    """Custom formatter that converts timestamps to market timezone"""
    
    def __init__(self, fmt=None, datefmt=None, timezone='America/New_York'):
        super().__init__(fmt, datefmt)
        self.timezone = pytz.timezone(timezone)
    
    def formatTime(self, record, datefmt=None):
        """Format time in the configured timezone"""
        dt = datetime.fromtimestamp(record.created, tz=pytz.UTC)
        dt = dt.astimezone(self.timezone)
        if datefmt:
            s = dt.strftime(datefmt)
        else:
            t = dt.timetuple()
            s = time.strftime(self.default_time_format, t)
            if self.default_msec_format:
                s = self.default_msec_format % (s, record.msecs)
        return s

def setup_logger(name: str, level=None) -> logging.Logger:
    """
    Setup a configured logger for the application
    
    Args:
        name: Logger name (usually __name__)
        level: Log level (default from Config.LOG_LEVEL)
    
    Returns:
        Configured logger instance
    """
    if level is None:
        level = getattr(logging, Config.LOG_LEVEL, logging.INFO)
    
    logger = logging.getLogger(name)
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger
    
    logger.setLevel(level)
    
    # Create logs directory
    log_dir = Config.LOG_DIR
    log_dir.mkdir(exist_ok=True)
    
    # File handler - one file per day
    log_date = datetime.now().strftime('%Y-%m-%d')
    log_file = log_dir / f"monitor_{log_date}.log"
    
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(level)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    
    # Timezone-aware formatter
    formatter = TimezoneFormatter(
        '[%(asctime)s] [%(levelname)-8s] [%(name)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        timezone=Config.MARKET_TIMEZONE
    )
    
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


# Create app-wide logger
app_logger = setup_logger("stop_loss_monitor")