#!/usr/bin/env python3
"""
Health Check Demo Script
Demonstrates the health check endpoints in action
"""
import time
import subprocess
import requests
import sys
from datetime import datetime

def test_health_endpoint(url, name):
    """Test a health endpoint"""
    try:
        response = requests.get(url, timeout=2)
        status_code = response.status_code
        
        if status_code == 200:
            print(f"✓ {name:30} (200 OK)")
            try:
                print(f"  Response: {response.json()}")
            except:
                print(f"  Response: {response.text}")
        elif status_code == 503:
            print(f"⚠ {name:30} (503 Service Unavailable)")
            print(f"  (Monitor not ready yet - check again in a few seconds)")
        else:
            print(f"✗ {name:30} ({status_code})")
            print(f"  Response: {response.text}")
        
        return status_code in [200, 503]  # Both are valid responses
    except requests.exceptions.ConnectionError:
        print(f"✗ {name:30} (Connection refused - Monitor not running)")
        print(f"  💡 Start the monitor first: python run_monitor.py")
        return False
    except Exception as e:
        print(f"✗ {name:30} (Error: {e})")
        return False


def main():
    """Run health check tests"""
    print("\n" + "=" * 70)
    print("Stop Loss Monitor - Health Check Endpoint Demo")
    print("=" * 70 + "\n")
    
    base_url = "http://localhost:5000"
    
    print("📋 Testing Health Check Endpoints\n")
    
    endpoints = [
        (f"{base_url}/health", "Basic Health Check"),
        (f"{base_url}/health/detailed", "Detailed Health Status"),
        (f"{base_url}/health/ready", "Readiness Probe"),
        (f"{base_url}/health/live", "Liveness Probe"),
    ]
    
    results = []
    for url, name in endpoints:
        time.sleep(0.5)  # Small delay between requests
        result = test_health_endpoint(url, name)
        results.append((name, result))
        print()
    
    # Summary
    print("=" * 70)
    passed = sum(1 for _, r in results if r)
    total = len(results)
    print(f"Results: {passed}/{total} endpoints responding\n")
    
    if passed == total:
        print("✅ All health checks passed!\n")
        print("📚 Documentation: See docs/HEALTH_CHECK.md for more details\n")
        return 0
    elif passed > 0:
        print("⚠️  Some endpoints are responding\n")
        print("💡 The monitor may still be initializing...\n")
        return 1
    else:
        print("❌ No endpoints responding\n")
        print("💡 Make sure the monitor is running:")
        print("   python run_monitor.py\n")
        print("   Then run this script in another terminal\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
