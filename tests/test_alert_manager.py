"""
Unit tests for AlertManager module
Tests position checking and alert coordination
"""
import unittest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import sys
import json

sys.path.insert(0, str(Path(__file__).parent.parent))


class TestAlertManager(unittest.TestCase):
    """Test alert manager"""
    
    @patch('modules.alert_manager.PositionReader')
    @patch('modules.alert_manager.StopLossValidator')
    @patch('modules.alert_manager.WhatsAppNotifier')
    def test_alert_manager_init(self, mock_notifier, mock_validator, mock_reader):
        """Test AlertManager initialization"""
        from modules.alert_manager import AlertManager
        
        manager = AlertManager("test-id", "mock_creds.json")
        
        self.assertIsNotNone(manager.position_reader)
        self.assertIsNotNone(manager.validator)
        self.assertIsNotNone(manager.notifier)
    
    @patch('modules.alert_manager.PositionReader')
    @patch('modules.alert_manager.StopLossValidator')
    @patch('modules.alert_manager.WhatsAppNotifier')
    def test_should_send_alert_first_time(self, mock_notifier, mock_validator, mock_reader):
        """Test that first alert for symbol is sent"""
        from modules.alert_manager import AlertManager
        
        manager = AlertManager("test-id", "mock_creds.json")
        
        should_send = manager._should_send_alert('AAPL')
        
        self.assertTrue(should_send)
    
    @patch('modules.alert_manager.PositionReader')
    @patch('modules.alert_manager.StopLossValidator')
    @patch('modules.alert_manager.WhatsAppNotifier')
    def test_alert_cooldown(self, mock_notifier, mock_validator, mock_reader):
        """Test alert cooldown prevents duplicate alerts"""
        from modules.alert_manager import AlertManager
        from datetime import datetime, timedelta
        
        manager = AlertManager("test-id", "mock_creds.json")
        
        # First alert sent
        manager.alert_history['AAPL'] = datetime.now()
        
        # Should not send again (in cooldown)
        should_send = manager._should_send_alert('AAPL')
        self.assertFalse(should_send)
        
        # Simulate cooldown passed
        manager.alert_history['AAPL'] = datetime.now() - timedelta(minutes=35)
        
        # Should send again
        should_send = manager._should_send_alert('AAPL')
        self.assertTrue(should_send)
    
    @patch('modules.alert_manager.PositionReader')
    @patch('modules.alert_manager.StopLossValidator')
    @patch('modules.alert_manager.WhatsAppNotifier')
    def test_check_positions(self, mock_notifier_class, mock_validator_class, mock_reader_class):
        """Test checking multiple positions"""
        from modules.alert_manager import AlertManager
        
        # Setup mocks
        mock_reader = MagicMock()
        mock_reader_class.return_value = mock_reader
        mock_reader.get_symbols.return_value = ['AAPL', 'TSLA']
        
        mock_validator = MagicMock()
        mock_validator_class.return_value = mock_validator
        
        # Mock position statuses
        mock_validator.get_position_status.side_effect = [
            {
                'symbol': 'AAPL',
                'current_price': 155.0,
                'weekly_low': 150.0,
                'hit': False,
                'buffer_pct': 3.33,
            },
            {
                'symbol': 'TSLA',
                'current_price': 248.0,
                'weekly_low': 250.0,
                'hit': True,
                'buffer_pct': -0.80,
            }
        ]
        
        mock_notifier = MagicMock()
        mock_notifier_class.return_value = mock_notifier
        mock_notifier.send_alert.return_value = True
        
        manager = AlertManager("test-id", "mock_creds.json")
        manager.position_reader = mock_reader
        manager.validator = mock_validator
        manager.notifier = mock_notifier
        
        results = manager.check_positions()
        
        self.assertEqual(len(results), 2)
        self.assertFalse(results['AAPL']['hit'])
        self.assertTrue(results['TSLA']['hit'])
    
    @patch('modules.alert_manager.PositionReader')
    @patch('modules.alert_manager.StopLossValidator')
    @patch('modules.alert_manager.WhatsAppNotifier')
    def test_status_summary(self, mock_notifier, mock_validator, mock_reader):
        """Test generating status summary"""
        from modules.alert_manager import AlertManager
        
        manager = AlertManager("test-id", "mock_creds.json")
        
        # Mock results
        results = {
            'AAPL': {'hit': False, 'buffer_pct': 10.0},
            'TSLA': {'hit': True, 'buffer_pct': -0.5},
            'MSFT': {'hit': False, 'buffer_pct': 3.0},
            'GOOGL': {'hit': False, 'buffer_pct': 1.5},  # At risk
        }
        
        summary = manager.get_status_summary(results)
        
        self.assertEqual(summary['total'], 4)
        self.assertEqual(summary['hit'], 1)
        self.assertEqual(summary['safe'], 3)


if __name__ == '__main__':
    unittest.main()