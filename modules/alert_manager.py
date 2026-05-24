"""
Alert Manager
Orchestrates position checks and alert notifications
Prevents duplicate alerts and maintains alert history
"""
from typing import List, Dict, Optional, Set
from datetime import datetime, timedelta
from pathlib import Path
import json
from config import get_logger, Config
from .position_reader import PositionReader
from .stop_loss_validator import StopLossValidator
from .whatsapp_notifier import WhatsAppNotifier

logger = get_logger(__name__)


class AlertManager:
    """Manage position monitoring and alerts"""
    
    def __init__(self, spreadsheet_id: str):
        """
        Initialize alert manager
        
        Args:
            spreadsheet_id: Google Sheet ID
        """
        self.position_reader = PositionReader(spreadsheet_id)
        self.validator = StopLossValidator()
        self.notifier = WhatsAppNotifier()
        
        # Alert tracking
        self.alert_history = {}  # symbol -> last_alert_time
        self.alert_cooldown = timedelta(minutes=Config.ALERT_COOLDOWN_MINUTES)
        self.history_file = Path(__file__).parent.parent / "logs" / "alert_history.json"
        
        self._load_alert_history()
    
    def _load_alert_history(self):
        """Load alert history from file"""
        try:
            if self.history_file.exists():
                with open(self.history_file) as f:
                    data = json.load(f)
                    # Convert ISO timestamps back to datetime
                    for symbol, timestamp_str in data.items():
                        self.alert_history[symbol] = datetime.fromisoformat(timestamp_str)
                logger.debug(f"Loaded alert history: {len(self.alert_history)} symbols")
        except Exception as e:
            logger.warning(f"Could not load alert history: {e}")
    
    def _save_alert_history(self):
        """Save alert history to file"""
        try:
            data = {
                symbol: timestamp.isoformat()
                for symbol, timestamp in self.alert_history.items()
            }
            self.history_file.parent.mkdir(exist_ok=True)
            with open(self.history_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save alert history: {e}")
    
    def _should_send_alert(self, symbol: str) -> bool:
        """
        Check if alert should be sent (respects cooldown period)
        
        Args:
            symbol: Stock symbol
        
        Returns:
            True if alert should be sent, False if in cooldown
        """
        if symbol not in self.alert_history:
            return True
        
        last_alert = self.alert_history[symbol]
        time_since_alert = datetime.now() - last_alert
        
        if time_since_alert < self.alert_cooldown:
            remaining = self.alert_cooldown - time_since_alert
            logger.debug(f"{symbol}: In alert cooldown ({remaining.total_seconds():.0f}s remaining)")
            return False
        
        return True
    
    def check_positions(self) -> Dict[str, Dict]:
        """
        Check all positions for stop loss hits
        
        Returns:
            Dict with results for each symbol
        """
        logger.info("=" * 60)
        logger.info("Starting position check cycle")
        logger.info("=" * 60)
        
        # Get positions from Google Sheet
        positions = self.position_reader.get_symbols()
        
        if not positions:
            logger.warning("No positions to check")
            return {}
        
        symbols_list = [p['symbol'] for p in positions]
        logger.info(f"Checking {len(positions)} positions: {', '.join(symbols_list)}")
        logger.info("-" * 60)
        
        results = {}
        alerts_sent = 0
        
        for i, position in enumerate(positions, 1):
            try:
                symbol = position['symbol']
                entry_price = position.get('entry_price')
                
                logger.info(f"[{i}/{len(positions)}] Processing {symbol}")
                
                # Get position status (with entry price)
                status = self.validator.get_position_status(symbol, entry_price)
                
                if not status:
                    logger.warning(f"    {symbol}: Could not fetch status")
                    continue
                
                results[symbol] = status
                
                # Check if stop loss hit and alert not in cooldown
                if status['hit']:
                    if self._should_send_alert(symbol):
                        logger.warning(f"    🚨 STOP LOSS HIT! Sending alert for {symbol}")
                        
                        # Send WhatsApp alert (with entry price)
                        if self.notifier.send_alert(
                            symbol,
                            status['current_price'],
                            status['weekly_low'],
                            entry_price
                        ):
                            # Update alert history
                            self.alert_history[symbol] = datetime.now()
                            self._save_alert_history()
                            alerts_sent += 1
                            logger.info(f"    ✓ Alert sent for {symbol}")
                        else:
                            logger.error(f"    ✗ Failed to send alert for {symbol}")
                    else:
                        logger.info(f"    ⏱️ {symbol}: In alert cooldown, skipping notification")
            
            except Exception as e:
                logger.error(f"    Error checking {symbol}: {e}")
        
        logger.info("-" * 60)
        logger.info(f"✓ Check complete: {len(results)} positions checked, {alerts_sent} alerts sent")
        return results
    
    def get_alert_history(self) -> Dict[str, datetime]:
        """Get alert send history"""
        return self.alert_history.copy()
    
    def get_status_summary(self, results: Dict) -> Dict:
        """
        Generate summary statistics from check results
        
        Args:
            results: Results dict from check_positions()
        
        Returns:
            Summary stats
        """
        if not results:
            return {
                'total': 0,
                'at_risk': 0,
                'safe': 0,
                'hit': 0
            }
        
        at_risk = sum(1 for r in results.values() if r.get('buffer_pct', 100) < 5)
        hit = sum(1 for r in results.values() if r.get('hit', False))
        safe = len(results) - at_risk - hit
        
        return {
            'total': len(results),
            'at_risk': at_risk,
            'safe': safe,
            'hit': hit
        }