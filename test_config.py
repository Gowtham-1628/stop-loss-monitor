"""
Phase 1 Testing Script
Validates setup and infrastructure before Phase 2 development
"""
import sys
from pathlib import Path
import subprocess

def check_python_version():
    """Check Python version is 3.8+"""
    print("\n1️⃣  Python Version Check")
    print("-" * 60)
    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"
    
    if version.major >= 3 and version.minor >= 8:
        print(f"   ✓ Python {version_str} (OK)")
        return True
    else:
        print(f"   ✗ Python {version_str} (Need 3.8+)")
        return False


def check_dependencies():
    """Check if required packages are installed"""
    print("\n2️⃣  Dependencies Check")
    print("-" * 60)
    
    required = [
        "dotenv",
        "google",
        "twilio",
        "apscheduler",
        "pandas",
        "numpy",
        "pytz"
    ]
    
    missing = []
    for package in required:
        try:
            __import__(package)
            print(f"   ✓ {package}")
        except ImportError:
            print(f"   ✗ {package} (NOT INSTALLED)")
            missing.append(package)
    
    if missing:
        print(f"\n   📌 Install missing packages:")
        print(f"      pip install -r requirements.txt")
        return False
    
    return True


def check_files_exist():
    """Check if required files exist"""
    print("\n3️⃣  Files Check")
    print("-" * 60)
    
    base_dir = Path(__file__).parent
    required_files = [
        ("requirements.txt", "Dependencies file"),
        (".env.example", "Environment template"),
        ("config.py", "Configuration module"),
    ]
    
    all_exist = True
    for filename, description in required_files:
        filepath = base_dir / filename
        if filepath.exists():
            print(f"   ✓ {filename:<25} ({description})")
        else:
            print(f"   ✗ {filename:<25} ({description}) - MISSING")
            all_exist = False
    
    return all_exist


def check_folders_exist():
    """Check if required folders exist"""
    print("\n4️⃣  Folders Check")
    print("-" * 60)
    
    base_dir = Path(__file__).parent
    required_folders = [
        ("modules", "Core modules"),
        ("tests", "Test files"),
        ("logs", "Log files"),
        ("docs", "Documentation"),
        ("data", "Data storage"),
        ("results", "Results output"),
    ]
    
    for folder_name, description in required_folders:
        folder = base_dir / folder_name
        if folder.exists():
            print(f"   ✓ {folder_name:<20} ({description})")
        else:
            print(f"   ✗ {folder_name:<20} ({description}) - MISSING")
            # Create it
            folder.mkdir(exist_ok=True)
            print(f"      → Created {folder_name}")
    
    return True


def check_env_file():
    """Check if .env file exists and contains required keys"""
    print("\n5️⃣  Environment Configuration Check")
    print("-" * 60)
    
    base_dir = Path(__file__).parent
    env_file = base_dir / ".env"
    
    if not env_file.exists():
        print(f"   ✗ .env file not found")
        print(f"\n   📌 Create .env file:")
        print(f"      cp .env.example .env")
        print(f"      # Then edit .env with your credentials")
        return False
    
    print(f"   ✓ .env file exists")
    
    # Read and validate keys
    required_keys = [
        "WEBULL_APP_KEY",
        "WEBULL_APP_SECRET",
        "GOOGLE_SPREADSHEET_ID",
        "TWILIO_ACCOUNT_SID",
        "TWILIO_AUTH_TOKEN",
        "TWILIO_FROM_PHONE",
        "TWILIO_TO_PHONE",
    ]
    
    with open(env_file) as f:
        env_content = f.read()
    
    missing_keys = []
    for key in required_keys:
        if key in env_content:
            # Check if value is placeholder
            if "your_" in env_content.split(f"{key}=")[1].split("\n")[0].lower():
                print(f"   ⚠️  {key:<30} (placeholder value)")
            else:
                print(f"   ✓ {key:<30} (configured)")
        else:
            print(f"   ✗ {key:<30} (missing)")
            missing_keys.append(key)
    
    if missing_keys:
        return False
    
    return True


def check_config_import():
    """Try to import config.py and validate it"""
    print("\n6️⃣  Config Module Check")
    print("-" * 60)
    
    try:
        from config import Config, get_logger
        print(f"   ✓ config.py imports successfully")
        
        # Test logger
        logger = get_logger("test")
        print(f"   ✓ Logger initialized")
        
        # Check config values
        print(f"\n   Configuration Summary:")
        print(f"   - Market Hours:       {Config.MARKET_OPEN_TIME} - {Config.MARKET_CLOSE_TIME} ({Config.MARKET_TIMEZONE})")
        print(f"   - Check Interval:     {Config.CHECK_INTERVAL_MINUTES} minutes")
        print(f"   - Alert Cooldown:     {Config.ALERT_COOLDOWN_MINUTES} minutes")
        print(f"   - Log Level:          {Config.LOG_LEVEL}")
        print(f"   - Google Sheet ID:    {Config.GOOGLE_SPREADSHEET_ID[:20]}...")
        
        return True
    
    except ImportError as e:
        print(f"   ✗ Failed to import config: {e}")
        return False
    except Exception as e:
        print(f"   ✗ Config validation error: {e}")
        return False


def check_webull_market_data():
    """Verify WebullMarketData class and its methods"""
    print("\n7️⃣  Webull Market Data Module Check")
    print("-" * 60)
    
    try:
        from modules.webull_market_data import WebullMarketData
        print(f"   ✓ WebullMarketData class imports successfully")
        
        # Instantiate the class
        market_data = WebullMarketData()
        print(f"   ✓ WebullMarketData instantiates successfully")
        
        # Check for required methods
        required_methods = [
            "get_current_price",
            "get_weekly_low",
            "get_historical_bars",
            "get_market_data",
        ]
        
        for method_name in required_methods:
            if hasattr(market_data, method_name):
                print(f"   ✓ {method_name}() exists")
            else:
                print(f"   ✗ {method_name}() missing")
        
        return True
    
    except ImportError as e:
        print(f"   ✗ Failed to import WebullMarketData: {e}")
        return False
    except Exception as e:
        print(f"   ✗ WebullMarketData validation error: {e}")
        return False


def check_requirements_file():
    """Validate requirements.txt is properly formatted"""
    print("\n8️⃣  Requirements File Check")
    print("-" * 60)
    
    base_dir = Path(__file__).parent
    req_file = base_dir / "requirements.txt"
    
    if not req_file.exists():
        print(f"   ✗ requirements.txt not found")
        return False
    
    print(f"   ✓ requirements.txt exists")
    
    with open(req_file) as f:
        lines = [line.strip() for line in f if line.strip() and not line.startswith("#")]
    
    print(f"   ✓ {len(lines)} packages defined:")
    for line in lines[:5]:
        print(f"      - {line}")
    if len(lines) > 5:
        print(f"      ... and {len(lines) - 5} more")
    
    return True


def print_summary(results):
    """Print test summary"""
    print("\n" + "=" * 60)
    print("PHASE 1 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    print(f"\n✓ Passed: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 Phase 1 Setup Complete!")
        print("\nNext steps:")
        print("  1. Configure your credentials in .env:")
        print("     - WEBULL_APP_KEY, WEBULL_APP_SECRET (from Webull portal)")
        print("     - GOOGLE_SPREADSHEET_ID, GOOGLE_CREDENTIALS_PATH (from Google Cloud)")
        print("     - TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_FROM_PHONE, TWILIO_TO_PHONE (from Twilio)")
        print("\n  2. Place Google credentials.json in project root")
        print("\n  3. Run Phase 2 development: Create modules/")
        return True
    else:
        print(f"\n⚠️  {total - passed} issue(s) to fix before Phase 2")
        print("\nFailed checks:")
        for name, result in results.items():
            if not result:
                print(f"  - {name}")
        return False


def main():
    print("\n" + "=" * 60)
    print("PHASE 1: SETUP & INFRASTRUCTURE TEST")
    print("=" * 60)
    
    results = {
        "Python Version": check_python_version(),
        "Dependencies": check_dependencies(),
        "Files": check_files_exist(),
        "Folders": check_folders_exist(),
        "Environment File": check_env_file(),
        "Config Module": check_config_import(),
        "Webull Market Data": check_webull_market_data(),
        "Requirements File": check_requirements_file(),
    }
    
    success = print_summary(results)
    
    print("\n" + "=" * 60 + "\n")
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())