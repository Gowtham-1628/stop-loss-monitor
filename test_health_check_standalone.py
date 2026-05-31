#!/usr/bin/env python3
"""
Standalone Health Check Server Test
Tests the health check server without running the full monitor
Useful for debugging and verification
"""
import threading
import time
import requests
import sys
from datetime import datetime

def test_standalone():
    """Test health check server standalone"""
    print("\n" + "=" * 70)
    print("Health Check Server - Standalone Test")
    print("=" * 70 + "\n")
    
    try:
        from modules.health_check import HealthCheckServer
    except ImportError as e:
        print(f"❌ Cannot import HealthCheckServer: {e}")
        print("   Make sure you're in the project root directory")
        return 1
    
    # Create and start server
    print("🚀 Starting health check server...\n")
    server = HealthCheckServer(host='localhost', port=5001)
    server.mark_ready()
    server.update_status(datetime.now(), {'total': 5, 'safe': 3, 'at_risk': 1, 'hit': 1})
    
    # Start in background
    thread = threading.Thread(target=server.run, args=(False,), daemon=True)
    thread.start()
    
    # Wait for server to start
    time.sleep(2)
    
    # Test endpoints
    print("📋 Testing endpoints on http://localhost:5001\n")
    
    endpoints = [
        ("http://localhost:5001/health", "Basic Health"),
        ("http://localhost:5001/health/detailed", "Detailed Status"),
        ("http://localhost:5001/health/ready", "Readiness Probe"),
        ("http://localhost:5001/health/live", "Liveness Probe"),
    ]
    
    results = []
    for url, name in endpoints:
        try:
            response = requests.get(url, timeout=2)
            status = "✓" if response.status_code == 200 else "⚠"
            print(f"{status} {name:25} ({response.status_code})")
            print(f"  {response.json()}\n")
            results.append(response.status_code == 200)
        except Exception as e:
            print(f"✗ {name:25} (Error: {e})\n")
            results.append(False)
    
    # Summary
    print("=" * 70)
    if all(results):
        print("✅ All endpoints working correctly!\n")
        print("🎉 Health check server is ready to use\n")
        return 0
    else:
        print("⚠️  Some endpoints had issues\n")
        return 1


if __name__ == "__main__":
    sys.exit(test_standalone())
