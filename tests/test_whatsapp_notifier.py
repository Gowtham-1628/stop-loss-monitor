"""
Unit tests for WhatsAppNotifier module
Tests Twilio WhatsApp integration with mocks
"""
import unittest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))


class TestWhatsAppNotifier(unittest.TestCase):
    """Test WhatsApp notifications"""
    
    @patch('modules.whatsapp_notifier.Client')
    def test_send_alert_success(self, mock_client_class):
        """Test successfully sending WhatsApp alert"""
        from modules.whatsapp_notifier import WhatsAppNotifier
        
        # Mock Twilio client
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        # Mock message response
        mock_message = MagicMock()
        mock_message.sid = "SM123456789"
        mock_client.messages.create.return_value = mock_message
        
        notifier = WhatsAppNotifier()
        notifier.client = mock_client
        
        success = notifier.send_alert('AAPL', 149.50, 150.00)
        
        self.assertTrue(success)
        mock_client.messages.create.assert_called_once()
    
    @patch('modules.whatsapp_notifier.Client')
    def test_alert_message_format(self, mock_client_class):
        """Test WhatsApp message format"""
        from modules.whatsapp_notifier import WhatsAppNotifier
        
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        mock_message = MagicMock()
        mock_message.sid = "SM123456789"
        mock_client.messages.create.return_value = mock_message
        
        notifier = WhatsAppNotifier()
        notifier.client = mock_client
        
        notifier.send_alert('AAPL', 149.50, 150.00)
        
        # Check that message was created with correct content
        call_args = mock_client.messages.create.call_args
        message_body = call_args.kwargs['body']
        
        self.assertIn('STOP LOSS HIT', message_body)
        self.assertIn('AAPL', message_body)
        self.assertIn('149.50', message_body)
        self.assertIn('150.00', message_body)
    
    @patch('modules.whatsapp_notifier.Client')
    def test_send_test_message_success(self, mock_client_class):
        """Test sending test message"""
        from modules.whatsapp_notifier import WhatsAppNotifier
        
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        mock_message = MagicMock()
        mock_message.sid = "SM123456789"
        mock_client.messages.create.return_value = mock_message
        
        notifier = WhatsAppNotifier()
        notifier.client = mock_client
        
        success = notifier.send_test_message()
        
        self.assertTrue(success)
        call_args = mock_client.messages.create.call_args
        message_body = call_args.kwargs['body']
        self.assertIn('Test Message', message_body)


class TestWhatsAppNotifierErrorHandling(unittest.TestCase):
    """Test error handling in WhatsAppNotifier"""
    
    @patch('modules.whatsapp_notifier.Client')
    def test_send_alert_failure(self, mock_client_class):
        """Test handling send failure"""
        from modules.whatsapp_notifier import WhatsAppNotifier
        
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        # Simulate send failure
        mock_client.messages.create.side_effect = Exception("Send failed")
        
        notifier = WhatsAppNotifier()
        notifier.client = mock_client
        
        success = notifier.send_alert('AAPL', 149.50, 150.00)
        
        self.assertFalse(success)


if __name__ == '__main__':
    unittest.main()