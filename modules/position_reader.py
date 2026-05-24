"""
Google Sheets Position Reader
Fetches open positions (symbols) from a public Google Sheet via CSV export
No authentication needed - sheet must be publicly readable
"""
from typing import List, Optional, Dict
from datetime import datetime, timedelta
from config import get_logger
import csv
from io import StringIO

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

logger = get_logger(__name__)


class PositionReader:
    """Read open positions from public Google Sheet"""
    
    def __init__(self, spreadsheet_id: str):
        """
        Initialize Google Sheets reader
        
        Args:
            spreadsheet_id: Google Sheet ID (from URL)
        """
        self.spreadsheet_id = spreadsheet_id
        self.csv_url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/export?format=csv"
        self.last_fetch = None
        self.cached_symbols = []
        self.cache_duration = timedelta(minutes=5)
        
        logger.info(f"✓ PositionReader initialized for spreadsheet: {spreadsheet_id}")
    
    def fetch_positions(self, sheet_range: str = "Sheet1!A:B") -> Optional[List[Dict]]:
        """
        Fetch symbols and entry prices from public Google Sheet
        
        Args:
            sheet_range: Ignored for CSV export (kept for API compatibility)
        
        Returns:
            List of dicts with symbol and entry_price, or None if failed
        """
        # Check cache
        if self._is_cache_valid():
            logger.debug(f"Using cached positions ({len(self.cached_symbols)} positions)")
            return self.cached_symbols
        
        if not REQUESTS_AVAILABLE:
            logger.error("requests library not available")
            return None
        
        try:
            response = requests.get(self.csv_url, timeout=10)
            response.raise_for_status()
            
            # Parse CSV
            csv_reader = csv.reader(StringIO(response.text))
            positions = []
            
            is_header = True
            for i, row in enumerate(csv_reader):
                if not row or not row[0].strip():
                    continue
                
                # Skip header row
                if is_header:
                    is_header = False
                    continue
                
                symbol = str(row[0]).strip().upper()
                
                # Skip invalid rows
                if not symbol or symbol.startswith('#'):
                    continue
                
                # Parse entry price
                try:
                    entry_price = float(row[1]) if len(row) > 1 and row[1].strip() else None
                except (ValueError, IndexError):
                    entry_price = None
                
                positions.append({
                    'symbol': symbol,
                    'entry_price': entry_price
                })
            
            # Update cache
            self.cached_symbols = positions
            self.last_fetch = datetime.now()
            
            logger.info(f"✓ Fetched {len(positions)} positions from Google Sheet")
            return positions
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch from Google Sheet: {e}")
            return None
        except Exception as e:
            logger.error(f"Error parsing positions: {e}")
            return None
    
    def _is_cache_valid(self) -> bool:
        """Check if cached data is still valid"""
        if not self.last_fetch or not self.cached_symbols:
            return False
        
        elapsed = datetime.now() - self.last_fetch
        return elapsed < self.cache_duration
    
    def get_symbols(self) -> List[Dict]:
        """
        Get list of positions with symbols and entry prices
        
        Returns:
            List of dicts with 'symbol' and 'entry_price' keys
        """
        positions = self.fetch_positions()
        return positions if positions else []
    
    def validate_sheet(self) -> bool:
        """Validate that sheet is accessible"""
        try:
            response = requests.head(self.csv_url, timeout=10)
            response.raise_for_status()
            logger.info(f"✓ Sheet accessible")
            return True
        except Exception as e:
            logger.error(f"Failed to access sheet: {e}")
            return False