"""
Webull API Market Data Fetcher
Fetches real-time quotes and historical bars
"""
from typing import Optional, Dict, List
import time
from datetime import datetime
import sys
from pathlib import Path

# Add parent directory to path to import notoken
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import get_logger, Config
import notoken

logger = get_logger(__name__)


class WebullMarketData:
    """Fetch market data from Webull API"""
    
    def __init__(self):
        """Initialize Webull API wrapper"""
        self.app_key = Config.WEBULL_APP_KEY
        self.app_secret = Config.WEBULL_APP_SECRET
        self.rate_limit_delay = 0.2  # 200ms between requests (300 req/min)
        self.last_request_time = 0
    
    def _rate_limit(self):
        """Apply rate limiting (300 requests/minute = 200ms per request)"""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - elapsed)
        self.last_request_time = time.time()
    
    def get_current_price(self, symbol: str) -> Optional[float]:
        """
        Get current price for a symbol
        
        Args:
            symbol: Stock symbol (e.g., "AAPL")
        
        Returns:
            Current price or None if failed
        """
        try:
            self._rate_limit()
            
            logger.debug(f"Fetching current price for {symbol}")
            
            # Use notoken's get_snapshot function
            data = notoken.get_snapshot(symbol=symbol)
            
            logger.debug(f"API returned type: {type(data)}, value: {data}")
            
            if data:
                # Parse response - structure depends on Webull API response
                # Typically: data['data']['quote']['last'] or similar
                price = self._parse_price(data)
                
                if price:
                    logger.debug(f"  {symbol}: ${price:.2f}")
                    return float(price)
            
            logger.warning(f"No price data for {symbol}")
            return None
        
        except Exception as e:
            logger.error(f"Failed to fetch price for {symbol}: {e}")
            return None
    
    def get_weekly_low(self, symbol: str, weeks: int = 2) -> Optional[float]:
        """
        Get the lowest price from the previous week (last calendar week, Mon-Sun)
        
        Args:
            symbol: Stock symbol
            weeks: Number of bars to fetch (2 = current week + previous week)
        
        Returns:
            Previous week's low price or None if failed
        """
        try:
            self._rate_limit()
            
            logger.debug(f"Fetching weekly low for {symbol}")
            
            # Fetch 2 weeks: current week + previous week
            data = notoken.get_historical_bars(
                symbol=symbol,
                timespan="W",  # Weekly
                count=weeks
            )
            
            # Data is returned as a list, most recent first
            if isinstance(data, list) and len(data) >= 2:
                # data[0] = current/latest week
                # data[1] = previous week (what we need)
                prev_week_bar = data[1]
                
                if isinstance(prev_week_bar, dict) and 'low' in prev_week_bar:
                    try:
                        prev_week_low = float(prev_week_bar['low'])
                        logger.debug(f"  {symbol}: Previous week low = ${prev_week_low:.2f}")
                        return prev_week_low
                    except (ValueError, TypeError):
                        pass
                
                logger.warning(f"No low data in previous week bar for {symbol}")
                return None
            
            logger.warning(f"Insufficient historical data for {symbol} (need 2+ weeks)")
            return None
        
        except Exception as e:
            logger.error(f"Failed to fetch weekly low for {symbol}: {e}")
            return None
    
    def get_historical_bars(self, symbol: str, timespan: str = "W", count: int = 52) -> Optional[List[Dict]]:
        """
        Get historical bars (OHLCV data)
        
        Args:
            symbol: Stock symbol
            timespan: "M1", "M5", "M15", "M30", "M60", "D", "W", "M", "Y"
            count: Number of bars to fetch
        
        Returns:
            List of bar data or None if failed
        """
        try:
            self._rate_limit()
            
            logger.debug(f"Fetching {count} {timespan} bars for {symbol}")
            
            data = notoken.get_historical_bars(
                symbol=symbol,
                timespan=timespan,
                count=count
            )
            
            # API returns list directly
            if isinstance(data, list):
                logger.debug(f"  {symbol}: Got {len(data)} bars")
                return data
            
            return None
        
        except Exception as e:
            logger.error(f"Failed to fetch bars for {symbol}: {e}")
            return None
    
    def get_market_data(self, symbol: str) -> Optional[Dict]:
        """
        Get comprehensive market data for a symbol
        
        Args:
            symbol: Stock symbol
        
        Returns:
            Dict with current_price and weekly_low or None
        """
        try:
            current_price = self.get_current_price(symbol)
            weekly_low = self.get_weekly_low(symbol)
            
            if current_price is not None and weekly_low is not None:
                return {
                    'symbol': symbol,
                    'current_price': current_price,
                    'weekly_low': weekly_low,
                    'timestamp': datetime.now().isoformat()
                }
            
            return None
        
        except Exception as e:
            logger.error(f"Failed to get market data for {symbol}: {e}")
            return None
    
    def _parse_price(self, data) -> Optional[float]:
        """
        Parse price from Webull API response
        Handles multiple response formats
        """
        try:
            # Handle list response (array of snapshot objects)
            if isinstance(data, list) and len(data) > 0:
                item = data[0]
                if isinstance(item, dict) and 'price' in item:
                    return float(item['price'])
            
            # Handle dict responses
            if isinstance(data, dict):
                # Try common response structures
                if 'data' in data and 'quote' in data['data']:
                    return data['data']['quote'].get('last')
                elif 'data' in data and 'last' in data['data']:
                    return data['data'].get('last')
                elif 'last' in data:
                    return data.get('last')
                elif 'price' in data:
                    return float(data['price'])
            
            return None
        except Exception as e:
            logger.debug(f"Price parsing error: {e}")
            return None