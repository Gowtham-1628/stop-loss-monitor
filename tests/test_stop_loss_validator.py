"""
Unit tests for StopLossValidator module
Tests stop loss detection logic
"""
import unittest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))


class TestStopLossValidator(unittest.TestCase):
    """Test stop loss validation logic"""
    
    @patch('modules.stop_loss_validator.WebullMarketData')
    def test_check_stop_loss_hit(self, mock_market_data_class):
        """Test detecting when stop loss is hit"""
        from modules.stop_loss_validator import StopLossValidator
        
        # Mock market data
        mock_market_data = MagicMock()
        mock_market_data_class.return_value = mock_market_data
        mock_market_data.get_weekly_low.return_value = 150.0
        
        validator = StopLossValidator()
        
        # Price below stop loss - HIT
        hit = validator.check_stop_loss_hit('AAPL', 149.50)
        self.assertTrue(hit)
    
    @patch('modules.stop_loss_validator.WebullMarketData')
    def test_check_stop_loss_not_hit(self, mock_market_data_class):
        """Test when stop loss is NOT hit"""
        from modules.stop_loss_validator import StopLossValidator
        
        mock_market_data = MagicMock()
        mock_market_data_class.return_value = mock_market_data
        mock_market_data.get_weekly_low.return_value = 150.0
        
        validator = StopLossValidator()
        
        # Price above stop loss - NOT HIT
        hit = validator.check_stop_loss_hit('AAPL', 150.50)
        self.assertFalse(hit)
    
    @patch('modules.stop_loss_validator.WebullMarketData')
    def test_check_stop_loss_at_exact_level(self, mock_market_data_class):
        """Test when price equals stop loss exactly"""
        from modules.stop_loss_validator import StopLossValidator
        
        mock_market_data = MagicMock()
        mock_market_data_class.return_value = mock_market_data
        mock_market_data.get_weekly_low.return_value = 150.0
        
        validator = StopLossValidator()
        
        # Price equals stop loss - IS HIT (<=)
        hit = validator.check_stop_loss_hit('AAPL', 150.00)
        self.assertTrue(hit)
    
    @patch('modules.stop_loss_validator.WebullMarketData')
    def test_get_position_status(self, mock_market_data_class):
        """Test getting complete position status"""
        from modules.stop_loss_validator import StopLossValidator
        
        mock_market_data = MagicMock()
        mock_market_data_class.return_value = mock_market_data
        mock_market_data.get_market_data.return_value = {
            'symbol': 'AAPL',
            'current_price': 155.0,
            'weekly_low': 150.0,
            'timestamp': '2026-05-23T14:30:00'
        }
        
        validator = StopLossValidator()
        status = validator.get_position_status('AAPL')
        
        self.assertIsNotNone(status)
        self.assertEqual(status['symbol'], 'AAPL')
        self.assertEqual(status['current_price'], 155.0)
        self.assertEqual(status['weekly_low'], 150.0)
        self.assertFalse(status['hit'])
        self.assertAlmostEqual(status['buffer_pct'], 3.33, places=1)
    
    @patch('modules.stop_loss_validator.WebullMarketData')
    def test_validate_multiple_positions(self, mock_market_data_class):
        """Test validating multiple positions at once"""
        from modules.stop_loss_validator import StopLossValidator
        
        mock_market_data = MagicMock()
        mock_market_data_class.return_value = mock_market_data
        
        # Mock returns for different symbols
        def mock_status(symbol):
            if symbol == 'AAPL':
                return {
                    'symbol': 'AAPL',
                    'current_price': 155.0,
                    'weekly_low': 150.0,
                    'hit': False,
                    'buffer_pct': 3.33,
                }
            elif symbol == 'TSLA':
                return {
                    'symbol': 'TSLA',
                    'current_price': 248.0,
                    'weekly_low': 250.0,
                    'hit': True,
                    'buffer_pct': -0.80,
                }
        
        mock_market_data.get_market_data.side_effect = mock_status
        validator = StopLossValidator()
        validator.market_data = mock_market_data
        validator.market_data.get_market_data = MagicMock(side_effect=mock_status)
        
        results = validator.validate_all_positions(['AAPL', 'TSLA'])
        
        self.assertEqual(len(results), 2)
        self.assertFalse(results['AAPL']['hit'])
        self.assertTrue(results['TSLA']['hit'])


if __name__ == '__main__':
    unittest.main()