"""
Integration Tests - End-to-End Testing
Tests complete workflow without real credentials
"""
import unittest
from unittest.mock import Mock, patch, MagicMock, call
from pathlib import Path
import sys
import json
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent))


class TestEndToEndWorkflow(unittest.TestCase):
    """Test complete monitoring workflow"""
    
    @patch('modules.alert_manager.PositionReader')
    @patch('modules.alert_manager.StopLossValidator')
    @patch('modules.alert_manager.WhatsAppNotifier')
    def test_full_check_cycle_no_alerts(self, mock_notifier_class, mock_validator_class, mock_reader_class):
        """Test complete check cycle with no stop losses hit"""
        from modules.alert_manager import AlertManager
        
        # Setup mocks
        mock_reader = MagicMock()
        mock_reader_class.return_value = mock_reader
        mock_reader.get_symbols.return_value = ['AAPL', 'MSFT', 'GOOGL']
        
        mock_validator = MagicMock()
        mock_validator_class.return_value = mock_validator
        
        # All positions safe
        mock_validator.get_position_status.side_effect = [
            {'symbol': 'AAPL', 'current_price': 155.0, 'weekly_low': 150.0, 'hit': False, 'buffer_pct': 3.33},
            {'symbol': 'MSFT', 'current_price': 420.0, 'weekly_low': 410.0, 'hit': False, 'buffer_pct': 2.44},
            {'symbol': 'GOOGL', 'current_price': 145.0, 'weekly_low': 140.0, 'hit': False, 'buffer_pct': 3.57},
        ]
        
        mock_notifier = MagicMock()
        mock_notifier_class.return_value = mock_notifier
        
        manager = AlertManager("test-id", "mock_creds.json")
        manager.position_reader = mock_reader
        manager.validator = mock_validator
        manager.notifier = mock_notifier
        
        results = manager.check_positions()
        summary = manager.get_status_summary(results)
        
        # Verify results
        self.assertEqual(len(results), 3)
        self.assertEqual(summary['total'], 3)
        self.assertEqual(summary['hit'], 0)
        self.assertEqual(summary['safe'], 3)
        
        # No alerts should be sent
        mock_notifier.send_alert.assert_not_called()
    
    @patch('modules.alert_manager.PositionReader')
    @patch('modules.alert_manager.StopLossValidator')
    @patch('modules.alert_manager.WhatsAppNotifier')
    def test_full_check_cycle_with_alerts(self, mock_notifier_class, mock_validator_class, mock_reader_class):
        """Test complete check cycle with stop losses hit"""
        from modules.alert_manager import AlertManager
        
        # Setup mocks
        mock_reader = MagicMock()
        mock_reader_class.return_value = mock_reader
        mock_reader.get_symbols.return_value = ['AAPL', 'TSLA']
        
        mock_validator = MagicMock()
        mock_validator_class.return_value = mock_validator
        
        # One position hit stop loss
        mock_validator.get_position_status.side_effect = [
            {'symbol': 'AAPL', 'current_price': 155.0, 'weekly_low': 150.0, 'hit': False, 'buffer_pct': 3.33},
            {'symbol': 'TSLA', 'current_price': 248.0, 'weekly_low': 250.0, 'hit': True, 'buffer_pct': -0.80},
        ]
        
        mock_notifier = MagicMock()
        mock_notifier_class.return_value = mock_notifier
        mock_notifier.send_alert.return_value = True
        
        manager = AlertManager("test-id", "mock_creds.json")
        manager.position_reader = mock_reader
        manager.validator = mock_validator
        manager.notifier = mock_notifier
        
        results = manager.check_positions()
        summary = manager.get_status_summary(results)
        
        # Verify results
        self.assertEqual(len(results), 2)
        self.assertEqual(summary['total'], 2)
        self.assertEqual(summary['hit'], 1)
        
        # Alert should be sent for TSLA
        mock_notifier.send_alert.assert_called_once()
        call_args = mock_notifier.send_alert.call_args
        self.assertEqual(call_args[0][0], 'TSLA')
    
    @patch('modules.alert_manager.PositionReader')
    @patch('modules.alert_manager.StopLossValidator')
    @patch('modules.alert_manager.WhatsAppNotifier')
    def test_duplicate_alert_prevention(self, mock_notifier_class, mock_validator_class, mock_reader_class):
        """Test that duplicate alerts are prevented within cooldown"""
        from modules.alert_manager import AlertManager
        
        # Setup mocks
        mock_reader = MagicMock()
        mock_reader_class.return_value = mock_reader
        mock_reader.get_symbols.return_value = ['TSLA']
        
        mock_validator = MagicMock()
        mock_validator_class.return_value = mock_validator
        mock_validator.get_position_status.return_value = {
            'symbol': 'TSLA',
            'current_price': 248.0,
            'weekly_low': 250.0,
            'hit': True,
            'buffer_pct': -0.80,
        }
        
        mock_notifier = MagicMock()
        mock_notifier_class.return_value = mock_notifier
        mock_notifier.send_alert.return_value = True
        
        manager = AlertManager("test-id", "mock_creds.json")
        manager.position_reader = mock_reader
        manager.validator = mock_validator
        manager.notifier = mock_notifier
        
        # First check - alert sent
        manager.check_positions()
        self.assertEqual(mock_notifier.send_alert.call_count, 1)
        
        # Second check immediately - alert NOT sent (cooldown)
        manager.check_positions()
        self.assertEqual(mock_notifier.send_alert.call_count, 1)  # Still 1
        
        # Simulate cooldown passed
        manager.alert_history['TSLA'] = datetime.now() - timedelta(minutes=35)
        
        # Third check - alert sent again
        manager.check_positions()
        self.assertEqual(mock_notifier.send_alert.call_count, 2)  # Now 2


class TestErrorRecovery(unittest.TestCase):
    """Test error handling and recovery"""
    
    @patch('modules.alert_manager.PositionReader')
    @patch('modules.alert_manager.StopLossValidator')
    @patch('modules.alert_manager.WhatsAppNotifier')
    def test_missing_position_data(self, mock_notifier_class, mock_validator_class, mock_reader_class):
        """Test handling when position data is missing"""
        from modules.alert_manager import AlertManager
        
        mock_reader = MagicMock()
        mock_reader_class.return_value = mock_reader
        mock_reader.get_symbols.return_value = ['AAPL', 'INVALID']
        
        mock_validator = MagicMock()
        mock_validator_class.return_value = mock_validator
        
        # One valid, one invalid
        mock_validator.get_position_status.side_effect = [
            {'symbol': 'AAPL', 'current_price': 155.0, 'weekly_low': 150.0, 'hit': False, 'buffer_pct': 3.33},
            None  # Invalid symbol returns None
        ]
        
        mock_notifier = MagicMock()
        mock_notifier_class.return_value = mock_notifier
        
        manager = AlertManager("test-id", "mock_creds.json")
        manager.position_reader = mock_reader
        manager.validator = mock_validator
        manager.notifier = mock_notifier
        
        results = manager.check_positions()
        
        # Should handle gracefully - only 1 result
        self.assertEqual(len(results), 1)
        self.assertIn('AAPL', results)
    
    @patch('modules.alert_manager.PositionReader')
    @patch('modules.alert_manager.StopLossValidator')
    @patch('modules.alert_manager.WhatsAppNotifier')
    def test_notification_failure_recovery(self, mock_notifier_class, mock_validator_class, mock_reader_class):
        """Test handling when notification fails"""
        from modules.alert_manager import AlertManager
        
        mock_reader = MagicMock()
        mock_reader_class.return_value = mock_reader
        mock_reader.get_symbols.return_value = ['TSLA']
        
        mock_validator = MagicMock()
        mock_validator_class.return_value = mock_validator
        mock_validator.get_position_status.return_value = {
            'symbol': 'TSLA',
            'current_price': 248.0,
            'weekly_low': 250.0,
            'hit': True,
            'buffer_pct': -0.80,
        }
        
        mock_notifier = MagicMock()
        mock_notifier_class.return_value = mock_notifier
        mock_notifier.send_alert.return_value = False  # Send fails
        
        manager = AlertManager("test-id", "mock_creds.json")
        manager.position_reader = mock_reader
        manager.validator = mock_validator
        manager.notifier = mock_notifier
        
        # Should complete without crashing
        results = manager.check_positions()
        
        self.assertEqual(len(results), 1)
        # Alert history should NOT be updated (send failed)
        self.assertNotIn('TSLA', manager.alert_history)


if __name__ == '__main__':
    unittest.main()