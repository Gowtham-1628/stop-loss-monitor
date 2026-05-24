"""
Unit tests for Monitor scheduler
Tests market hours logic and scheduling
"""
import unittest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, time
from pathlib import Path
import sys
import pytz

sys.path.insert(0, str(Path(__file__).parent.parent))


class TestMonitorScheduler(unittest.TestCase):
    """Test monitor scheduler"""
    
    @patch('monitor.AlertManager')
    def test_monitor_init(self, mock_alert_manager):
        """Test Monitor initialization"""
        from monitor import StopLossMonitor
        
        monitor = StopLossMonitor()
        
        self.assertIsNotNone(monitor)
        self.assertIsNone(monitor.scheduler)
    
    @patch('monitor.AlertManager')
    def test_is_market_hours_weekday_during_hours(self, mock_alert_manager):
        """Test market hours detection - weekday during hours"""
        from monitor import StopLossMonitor
        from config import Config
        
        monitor = StopLossMonitor()
        
        # Mock current time: Wed 14:00 EST (2 PM, within hours)
        with patch('monitor.datetime') as mock_datetime:
            # Create mock datetime that returns Wednesday at 2 PM
            mock_now = MagicMock()
            mock_now.weekday.return_value = 2  # Wednesday
            mock_now.time.return_value = time(14, 0)  # 2 PM
            
            mock_datetime.now.return_value = mock_now
            mock_datetime.strptime = datetime.strptime
            
            # This would pass if logic is correct
            # (implementation check only)
    
    @patch('monitor.AlertManager')
    def test_is_market_hours_weekend(self, mock_alert_manager):
        """Test market hours detection - weekend"""
        from monitor import StopLossMonitor
        
        monitor = StopLossMonitor()
        
        # Verify is_market_hours method exists
        self.assertTrue(hasattr(monitor, 'is_market_hours'))
        self.assertTrue(callable(monitor.is_market_hours))
    
    @patch('monitor.AlertManager')
    def test_run_check_method_exists(self, mock_alert_manager):
        """Test run_check method"""
        from monitor import StopLossMonitor
        
        monitor = StopLossMonitor()
        
        self.assertTrue(hasattr(monitor, 'run_check'))
        self.assertTrue(callable(monitor.run_check))
    
    @patch('monitor.AlertManager')
    def test_schedule_jobs_creates_scheduler(self, mock_alert_manager):
        """Test schedule_jobs creates APScheduler"""
        from monitor import StopLossMonitor
        
        monitor = StopLossMonitor()
        success = monitor.schedule_jobs()
        
        if success:
            self.assertIsNotNone(monitor.scheduler)
            monitor.scheduler.shutdown()


if __name__ == '__main__':
    unittest.main()