# Quick validation script
from modules.webull_market_data import WebullMarketData
from config import Config

def test_webull_connectivity():
    print("Testing Webull API connectivity...")
    
    fetcher = WebullMarketData()
    
    # Test with real AAPL (most liquid)
    price = fetcher.get_current_price('AAPL')
    
    if price:
        print(f"✅ AAPL price: ${price:.2f}")
        return True
    else:
        print(f"❌ Could not fetch price")
        return False

if __name__ == "__main__":
    success = test_webull_connectivity()
    exit(0 if success else 1)