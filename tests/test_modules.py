"""
Unit tests for Phase 2 modules
"""
import unittest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import sys

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import Config


class TestWebullMarketData(unittest.TestCase):
    """Test Webull market data module"""
    
    def test_import(self):
        """Test module imports"""
        from modules.webull_market_data import WebullMarketData
        self.assertIsNotNone(WebullMarketData)
    
    @patch('modules.webull_market_data.notoken')
    def test_get_current_price(self, mock_notoken):
        """Test fetching current price"""
        from modules.webull_market_data import WebullMarketData
        
        # Mock notoken response
        mock_notoken.get_snapshot.return_value = {
            'data': {'quote': {'last': 150.25}}
        }
        
        fetcher = WebullMarketData()
        price = fetcher.get_current_price('AAPL')
        
        self.assertEqual(price, 150.25)


class TestStopLossValidator(unittest.TestCase):
    """Test stop loss validator module"""
    
    def test_import(self):
        """Test module imports"""
        from modules.stop_loss_validator import StopLossValidator
        self.assertIsNotNone(StopLossValidator)
    
    def test_validator_creation(self):
        """Test validator initialization"""
        from modules.stop_loss_validator import StopLossValidator
        
        validator = StopLossValidator()
        self.assertIsNotNone(validator)


class TestWhatsAppNotifier(unittest.TestCase):
    """Test WhatsApp notifier module"""
    
    def test_import(self):
        """Test module imports"""
        from modules.whatsapp_notifier import WhatsAppNotifier
        self.assertIsNotNone(WhatsAppNotifier)


class TestAlertManager(unittest.TestCase):
    """Test alert manager module"""
    
    def test_import(self):
        """Test module imports"""
        from modules.alert_manager import AlertManager
        self.assertIsNotNone(AlertManager)


if __name__ == '__main__':
    unittest.main()