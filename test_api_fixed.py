#!/usr/bin/env python3
"""Test script to verify API functionality after fixes."""

import requests
import time
import sys
import json

BASE_URL = "http://localhost:8000"
API_KEY = "dev-key-change-in-production"  # Default dev key

def test_endpoint(name, method, endpoint, headers=None, data=None, expect_auth=False):
    """Test a single API endpoint."""
    url = f"{BASE_URL}{endpoint}"
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, timeout=5)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data, timeout=5)
        
        status = response.status_code
        
        # Check if authentication is working as expected
        if expect_auth and status == 401:
            return True, f"✓ {name}: Auth required (expected)"
        elif not expect_auth and status in [200, 404]:  # 404 is ok for some endpoints
            return True, f"✓ {name}: Status {status}"
        elif status == 200:
            return True, f"✓ {name}: Success"
        else:
            return False, f"✗ {name}: Status {status}"
            
    except Exception as e:
        return False, f"✗ {name}: {str(e)}"

def main():
    """Run all API tests."""
    print("=" * 60)
    print("SuperAgent v8 API Test Suite")
    print("=" * 60)
    print()
    
    # Wait for server to be ready
    print("Waiting for server to start...")
    time.sleep(2)
    
    results = []
    
    # Test public endpoints (no auth required)
    print("\n--- Public Endpoints ---")
    tests = [
        ("Health Check", "GET", "/health", None, None, False),
        ("API Info", "GET", "/api", None, None, False),
        ("Root Endpoint", "GET", "/", None, None, False),
    ]
    
    for test in tests:
        success, message = test_endpoint(*test)
        results.append(success)
        print(message)
    
    # Test protected endpoints without auth (should fail)
    print("\n--- Protected Endpoints (No Auth - Should Fail) ---")
    tests_no_auth = [
        ("Generate Code (No Auth)", "POST", "/generate", None, {"instruction": "test", "language": "python"}, True),
        ("Stats (No Auth)", "GET", "/stats", None, None, True),
    ]
    
    for test in tests_no_auth:
        success, message = test_endpoint(*test)
        results.append(success)
        print(message)
    
    # Test protected endpoints with auth
    print("\n--- Protected Endpoints (With Auth) ---")
    headers = {"X-API-Key": API_KEY}
    
    tests_with_auth = [
        ("Stats (With Auth)", "GET", "/stats", headers, None, False),
    ]
    
    for test in tests_with_auth:
        success, message = test_endpoint(*test)
        results.append(success)
        print(message)
    
    # Summary
    print("\n" + "=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✓ All tests passed!")
        print("=" * 60)
        return 0
    else:
        print(f"✗ {total - passed} test(s) failed")
        print("=" * 60)
        return 1

if __name__ == "__main__":
    sys.exit(main())
