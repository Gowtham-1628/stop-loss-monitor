"""
Stop Loss Monitor - Main Application
Schedules position checks during market hours
Sleeps after 4 PM EST until 9:30 AM next day
"""
import sys
from pathlib import Path
from datetime import datetime, time
import pytz
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from config import Config, get_logger
from modules import AlertManager, HealthCheckServer

logger = get_logger(__name__)


class StopLossMonitor:
    """Main monitoring application"""
    
    def __init__(self):
        """Initialize monitor"""
        self.scheduler = None
        self.alert_manager = None
        self.health_server = None
        self.health_thread = None
        self.tz = pytz.timezone(Config.MARKET_TIMEZONE)
        
        logger.info("=" * 70)
        logger.info("Stop Loss Monitor Initialized")
        logger.info("=" * 70)
    
    def initialize_manager(self) -> bool:
        """Initialize alert manager with Google Sheets"""
        try:
            logger.info("Initializing Alert Manager...")
            
            self.alert_manager = AlertManager(
                spreadsheet_id=Config.GOOGLE_SPREADSHEET_ID
            )
            
            logger.info("✓ Alert Manager initialized")
            return True
        
        except Exception as e:
            logger.error(f"Failed to initialize Alert Manager: {e}")
            return False
    
    def is_market_hours(self) -> bool:
        """
        Check if current time is within market hours
        Market hours: 9:30 AM - 4:00 PM EST on weekdays
        
        Returns:
            True if within market hours, False otherwise
        """
        now = datetime.now(self.tz)
        
        # Check if weekday (Monday=0, Friday=4)
        if now.weekday() >= 5:  # Saturday or Sunday
            logger.debug(f"Weekend - market closed")
            return False
        
        market_open = datetime.strptime(Config.MARKET_OPEN_TIME, "%H:%M").time()
        market_close = datetime.strptime(Config.MARKET_CLOSE_TIME, "%H:%M").time()
        
        current_time = now.time()
        
        is_open = market_open <= current_time < market_close
        
        if not is_open:
            next_open = "Tomorrow 9:30 AM EST" if now.weekday() < 4 else "Monday 9:30 AM EST"
            logger.debug(f"Market closed - next open: {next_open}")
        
        return is_open
    
    def run_check(self):
        """
        Execute one check cycle
        Only runs if market is open, otherwise sleeps
        """
        if not self.is_market_hours():
            logger.info("⏰ Market hours check skipped - sleeping")
            return
        
        try:
            logger.info(f"⏱️  Running position check cycle...")
            
            if not self.alert_manager:
                logger.error("Alert manager not initialized")
                return
            
            # Check all positions
            results = self.alert_manager.check_positions()
            
            # Generate summary
            summary = self.alert_manager.get_status_summary(results)
            
            logger.info(
                f"✓ Check complete: "
                f"{summary['total']} positions | "
                f"{summary['safe']} safe | "
                f"{summary['at_risk']} at risk | "
                f"{summary['hit']} hit"
            )
            
            # Update health check endpoint
            if self.health_server:
                self.health_server.update_status(datetime.now(self.tz), summary)
        
        except Exception as e:
            logger.error(f"Error during check cycle: {e}")
    
    def schedule_jobs(self):
        """Setup APScheduler for periodic checks"""
        try:
            logger.info("Setting up scheduler...")
            
            # Create scheduler
            self.scheduler = BackgroundScheduler(timezone=Config.MARKET_TIMEZONE)
            
            # Add job to run every N minutes during market hours
            # Runs Monday-Friday, 9:30 AM - 4:00 PM EST
            self.scheduler.add_job(
                self.run_check,
                trigger=CronTrigger(
                    day_of_week='mon-fri',
                    hour='9-15',  # 9 AM - 3 PM (before 4 PM)
                    minute=f'*/{ Config.CHECK_INTERVAL_MINUTES}',
                    timezone=Config.MARKET_TIMEZONE
                ),
                id='position_check',
                name='Position Check',
                replace_existing=True
            )
            
            logger.info(
                f"✓ Scheduler configured: "
                f"Every {Config.CHECK_INTERVAL_MINUTES} minutes "
                f"({Config.MARKET_OPEN_TIME} - {Config.MARKET_CLOSE_TIME} EST, M-F)"
            )
            
            return True
        
        except Exception as e:
            logger.error(f"Failed to setup scheduler: {e}")
            return False
    
    def start(self):
        """Start the monitoring application"""
        try:
            # Validate configuration
            if not Config.validate():
                logger.error("Configuration validation failed")
                return False
            
            Config.print_config()
            
            # Initialize health check server
            try:
                self.health_server = HealthCheckServer(host="0.0.0.0", port=5000)
                self.health_thread = self.health_server.start_async(debug=False)
            except Exception as e:
                logger.warning(f"Could not start health check server: {e}")
                logger.warning("Monitor will continue without health endpoint")
            
            # Initialize alert manager
            if not self.initialize_manager():
                logger.error("Failed to initialize alert manager")
                return False
            
            # Schedule jobs
            if not self.schedule_jobs():
                logger.error("Failed to schedule jobs")
                return False
            
            # Mark monitor as ready
            if self.health_server:
                self.health_server.mark_ready()
            
            # Start scheduler
            self.scheduler.start()
            logger.info("🚀 Monitor started - watching for stop losses")
            logger.info(f"Running in background... Press Ctrl+C to stop")
            
            # Keep running
            try:
                while True:
                    import time
                    time.sleep(1)
            except KeyboardInterrupt:
                logger.info("\n🛑 Shutting down...")
                self.stop()
            
            return True
        
        except Exception as e:
            logger.error(f"Failed to start monitor: {e}")
            return False
    
    def stop(self):
        """Stop the monitor gracefully"""
        if self.scheduler:
            self.scheduler.shutdown()
            logger.info("✓ Scheduler stopped")
        logger.info("✓ Monitor stopped")


def main():
    """Main entry point"""
    logger.info("Starting Stop Loss Monitor")
    
    monitor = StopLossMonitor()
    success = monitor.start()
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())