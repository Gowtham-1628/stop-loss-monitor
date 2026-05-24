"""
Centralized Logging System
Logs all monitoring activities, checks, and alerts
"""
from pathlib import Path
import logging
from datetime import datetime
from config import Config

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
    
    # Formatter
    formatter = logging.Formatter(
        '[%(asctime)s] [%(levelname)-8s] [%(name)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


# Create app-wide logger
app_logger = setup_logger("stop_loss_monitor")