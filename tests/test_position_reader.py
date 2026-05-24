"""
Unit tests for PositionReader module
Tests Google Sheets integration with mocks (no real credentials needed)
"""
import unittest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from datetime import datetime, timedelta


class TestPositionReader(unittest.TestCase):
    """Test position reader without real Google Sheets"""
    
    @patch('modules.position_reader.build')
    def test_position_reader_init(self, mock_build):
        """Test PositionReader initialization"""
        from modules.position_reader import PositionReader
        
        # Mock service
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        
        reader = PositionReader(
            spreadsheet_id="test-id",
            credentials_path="mock_creds.json"
        )
        
        self.assertEqual(reader.spreadsheet_id, "test-id")
        self.assertIsNotNone(reader)
    
    @patch('modules.position_reader.build')
    def test_fetch_positions_success(self, mock_build):
        """Test successfully fetching positions"""
        from modules.position_reader import PositionReader
        
        # Mock service and response
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        
        mock_response = {
            'values': [
                ['AAPL'],
                ['MSFT'],
                ['GOOGL'],
                ['TSLA'],
            ]
        }
        
        mock_service.spreadsheets().values().get().execute.return_value = mock_response
        
        reader = PositionReader("test-id", "mock_creds.json")
        reader.service = mock_service
        
        symbols = reader.fetch_positions()
        
        self.assertEqual(len(symbols), 4)
        self.assertIn('AAPL', symbols)
        self.assertIn('MSFT', symbols)
        self.assertIn('GOOGL', symbols)
        self.assertIn('TSLA', symbols)
    
    @patch('modules.position_reader.build')
    def test_fetch_positions_empty_sheet(self, mock_build):
        """Test handling empty Google Sheet"""
        from modules.position_reader import PositionReader
        
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        
        # Empty sheet
        mock_response = {'values': []}
        mock_service.spreadsheets().values().get().execute.return_value = mock_response
        
        reader = PositionReader("test-id", "mock_creds.json")
        reader.service = mock_service
        
        symbols = reader.fetch_positions()
        
        self.assertEqual(len(symbols), 0)
    
    @patch('modules.position_reader.build')
    def test_cache_validity(self, mock_build):
        """Test position caching"""
        from modules.position_reader import PositionReader
        
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        
        mock_response = {'values': [['AAPL'], ['MSFT']]}
        mock_service.spreadsheets().values().get().execute.return_value = mock_response
        
        reader = PositionReader("test-id", "mock_creds.json")
        reader.service = mock_service
        
        # First fetch
        symbols1 = reader.fetch_positions()
        self.assertEqual(len(symbols1), 2)
        
        # Second fetch should use cache (service not called again)
        symbols2 = reader.fetch_positions()
        self.assertEqual(len(symbols2), 2)
        
        # Cache should be valid
        self.assertTrue(reader._is_cache_valid())


class TestPositionReaderErrorHandling(unittest.TestCase):
    """Test error handling in PositionReader"""
    
    @patch('modules.position_reader.build')
    def test_auth_failure(self, mock_build):
        """Test handling auth failure"""
        from modules.position_reader import PositionReader
        
        mock_build.side_effect = Exception("Auth failed")
        
        reader = PositionReader("test-id", "mock_creds.json")
        
        # Service should be None
        self.assertIsNone(reader.service)
    
    @patch('modules.position_reader.build')
    def test_api_error_handling(self, mock_build):
        """Test handling API errors"""
        from modules.position_reader import PositionReader
        
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        
        # Simulate API error
        mock_service.spreadsheets().values().get().execute.side_effect = Exception("API Error")
        
        reader = PositionReader("test-id", "mock_creds.json")
        reader.service = mock_service
        
        symbols = reader.fetch_positions()
        
        self.assertIsNone(symbols)


if __name__ == '__main__':
    unittest.main()