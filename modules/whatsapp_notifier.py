"""
WhatsApp Notifier
Sends stop loss alerts via WhatsApp using Twilio
"""
from typing import Optional, Dict
from datetime import datetime
from config import get_logger, Config

try:
    from twilio.rest import Client
    TWILIO_AVAILABLE = True
except ImportError:
    TWILIO_AVAILABLE = False

logger = get_logger(__name__)


class WhatsAppNotifier:
    """Send WhatsApp notifications via Twilio"""
    
    def __init__(self):
        """Initialize Twilio client"""
        self.account_sid = Config.TWILIO_ACCOUNT_SID
        self.auth_token = Config.TWILIO_AUTH_TOKEN
        self.from_phone = Config.TWILIO_FROM_PHONE
        self.to_phone = Config.TWILIO_TO_PHONE
        self.client = None
        
        self._authenticate()
    
    def _authenticate(self) -> bool:
        """Authenticate with Twilio"""
        if not TWILIO_AVAILABLE:
            logger.error("Twilio library not installed")
            return False
        
        if not all([self.account_sid, self.auth_token, self.from_phone, self.to_phone]):
            logger.error("Missing Twilio credentials")
            return False
        
        try:
            self.client = Client(self.account_sid, self.auth_token)
            logger.info("✓ Authenticated with Twilio")
            return True
        
        except Exception as e:
            logger.error(f"Twilio authentication failed: {e}")
            return False
    
    def send_alert(self, symbol: str, current_price: float, weekly_low: float, entry_price: float = None) -> bool:
        """
        Send WhatsApp stop loss alert
        
        Args:
            symbol: Stock symbol
            current_price: Current price
            weekly_low: Weekly low (stop loss level)
            entry_price: Entry price (optional)
        
        Returns:
            True if sent successfully, False otherwise
        """
        if not self.client:
            logger.error("Not authenticated with Twilio")
            return False
        
        try:
            # Format message
            message_body = (
                f"🚨 STOP LOSS HIT\n\n"
                f"Symbol: {symbol}\n"
                f"Current: ${current_price:.2f}\n"
            )
            
            # Add entry price if available
            if entry_price:
                entry_threshold = 0.9 * entry_price
                message_body += f"Entry Price: ${entry_price:.2f}\n"
                message_body += f"Entry Threshold (90%): ${entry_threshold:.2f}\n"
            
            message_body += (
                f"Stop Loss (Weekly Low): ${weekly_low:.2f}\n"
                f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S EST')}\n\n"
                f"⚠️ ACTION REQUIRED: Review position"
            )
            
            # Send via WhatsApp
            message = self.client.messages.create(
                from_=f"whatsapp:{self.from_phone}",
                body=message_body,
                to=f"whatsapp:{self.to_phone}"
            )
            
            logger.info(f"✓ WhatsApp alert sent: {symbol} (SID: {message.sid})")
            return True
        
        except Exception as e:
            logger.error(f"Failed to send WhatsApp alert for {symbol}: {e}")
            return False
    
    def send_test_message(self) -> bool:
        """Send a test message to verify Twilio is working"""
        if not self.client:
            logger.error("Not authenticated with Twilio")
            return False
        
        try:
            message_body = (
                f"✅ Stop Loss Monitor Test Message\n\n"
                f"This is a test notification sent at {datetime.now().strftime('%Y-%m-%d %H:%M:%S EST')}\n\n"
                f"If you received this, WhatsApp notifications are working!"
            )
            
            message = self.client.messages.create(
                from_=f"whatsapp:{self.from_phone}",
                body=message_body,
                to=f"whatsapp:{self.to_phone}"
            )
            
            logger.info(f"✓ Test message sent (SID: {message.sid})")
            return True
        
        except Exception as e:
            logger.error(f"Failed to send test message: {e}")
            return False