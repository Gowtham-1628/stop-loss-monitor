"""
Stop Loss Validator
Checks if current price has hit the weekly low stop loss
"""
from typing import Optional, Dict
from datetime import datetime
from config import get_logger
from .webull_market_data import WebullMarketData

logger = get_logger(__name__)


class StopLossValidator:
    """Validate if stop loss conditions are met"""
    
    def __init__(self):
        """Initialize validator with market data fetcher"""
        self.market_data = WebullMarketData()
    
    def calculate_stop_loss(self, symbol: str) -> Optional[float]:
        """
        Calculate stop loss as the weekly low
        
        Args:
            symbol: Stock symbol
        
        Returns:
            Weekly low (stop loss level) or None if failed
        """
        try:
            weekly_low = self.market_data.get_weekly_low(symbol)
            
            if weekly_low:
                logger.debug(f"{symbol}: Stop loss level = ${weekly_low:.2f}")
                return weekly_low
            
            logger.warning(f"{symbol}: Could not calculate stop loss")
            return None
        
        except Exception as e:
            logger.error(f"{symbol}: Error calculating stop loss: {e}")
            return None
    
    def check_stop_loss_hit(self, symbol: str, current_price: float) -> bool:
        """
        Check if current price has hit or fallen below stop loss
        
        Args:
            symbol: Stock symbol
            current_price: Current stock price
        
        Returns:
            True if stop loss is hit, False otherwise
        """
        try:
            stop_loss = self.calculate_stop_loss(symbol)
            
            if stop_loss is None:
                logger.warning(f"{symbol}: Cannot determine stop loss status")
                return False
            
            hit = current_price <= stop_loss
            
            if hit:
                logger.warning(f"🚨 STOP LOSS HIT: {symbol} | Price: ${current_price:.2f} <= Stop: ${stop_loss:.2f}")
            else:
                logger.debug(f"{symbol}: OK | Price: ${current_price:.2f} > Stop: ${stop_loss:.2f}")
            
            return hit
        
        except Exception as e:
            logger.error(f"{symbol}: Error checking stop loss: {e}")
            return False
    
    def get_position_status(self, symbol: str, entry_price: float = None) -> Optional[Dict]:
        """
        Get complete status of a position
        
        Args:
            symbol: Stock symbol
            entry_price: Entry price (optional, for threshold calculation)
        
        Returns:
            Dict with symbol, current_price, weekly_low, entry_price, hit status or None
        """
        try:
            logger.info(f"  Checking {symbol}...")
            
            market_data = self.market_data.get_market_data(symbol)
            
            if not market_data:
                logger.warning(f"    {symbol}: Could not fetch market data")
                return None
            
            current_price = market_data['current_price']
            weekly_low = market_data['weekly_low']
            
            # Calculate stop loss threshold
            # Stop loss is triggered if:
            # 1. current_price <= 0.9 * entry_price (10% drop from entry)
            # 2. OR current_price <= weekly_low (drops below previous week low)
            stop_loss_threshold = min(
                0.9 * entry_price if entry_price else float('inf'),
                weekly_low
            )
            
            is_hit = current_price <= stop_loss_threshold
            
            # Calculate buffer percentage
            buffer_pct = ((current_price - stop_loss_threshold) / stop_loss_threshold * 100)
            
            # Log detailed price comparison
            status_icon = "🚨" if is_hit else "✓"
            
            if entry_price:
                entry_threshold = 0.9 * entry_price
                weekly_threshold = weekly_low
                logger.info(f"    {status_icon} {symbol}: Current ${current_price:.2f} | Entry Threshold: ${entry_threshold:.2f} | Weekly Low: ${weekly_threshold:.2f} (Buffer: {buffer_pct:+.1f}%)")
            else:
                logger.info(f"    {status_icon} {symbol}: Current ${current_price:.2f} vs Low ${weekly_low:.2f} (Buffer: {buffer_pct:+.1f}%)")
            
            status = {
                'symbol': symbol,
                'current_price': current_price,
                'entry_price': entry_price,
                'weekly_low': weekly_low,
                'stop_loss_threshold': stop_loss_threshold,
                'hit': is_hit,
                'buffer_pct': buffer_pct,
                'timestamp': datetime.now().isoformat()
            }
            
            return status
        
        except Exception as e:
            logger.error(f"    {symbol}: Error getting position status: {e}")
            return None
    
    def validate_all_positions(self, symbols: list) -> Dict[str, Dict]:
        """
        Validate all positions at once
        
        Args:
            symbols: List of stock symbols
        
        Returns:
            Dict with symbol->status mapping
        """
        results = {}
        
        for symbol in symbols:
            status = self.get_position_status(symbol)
            if status:
                results[symbol] = status
        
        return results