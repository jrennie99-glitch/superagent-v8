#!/usr/bin/env python3.11
"""
Comprehensive Test Suite for SuperAgent v8
Tests all major features and endpoints
"""
import requests
import json
import time
from typing import Dict, List, Tuple

BASE_URL = "http://localhost:8000"

class TestResults:
    def __init__(self):
        self.passed = []
        self.failed = []
        self.warnings = []
        self.skipped = []
    
    def add_pass(self, test_name: str, details: str = ""):
        self.passed.append({"test": test_name, "details": details})
        print(f"✅ PASS: {test_name}")
        if details:
            print(f"   {details}")
    
    def add_fail(self, test_name: str, error: str):
        self.failed.append({"test": test_name, "error": error})
        print(f"❌ FAIL: {test_name}")
        print(f"   Error: {error}")
    
    def add_warning(self, test_name: str, message: str):
        self.warnings.append({"test": test_name, "message": message})
        print(f"⚠️  WARN: {test_name}")
        print(f"   {message}")
    
    def add_skip(self, test_name: str, reason: str):
        self.skipped.append({"test": test_name, "reason": reason})
        print(f"⏭️  SKIP: {test_name}")
        print(f"   Reason: {reason}")
    
    def summary(self):
        total = len(self.passed) + len(self.failed) + len(self.warnings) + len(self.skipped)
        print("\n" + "="*70)
        print("TEST SUMMARY")
        print("="*70)
        print(f"Total Tests: {total}")
        print(f"✅ Passed: {len(self.passed)}")
        print(f"❌ Failed: {len(self.failed)}")
        print(f"⚠️  Warnings: {len(self.warnings)}")
        print(f"⏭️  Skipped: {len(self.skipped)}")
        print("="*70)
        
        if self.failed:
            print("\n❌ FAILED TESTS:")
            for fail in self.failed:
                print(f"  - {fail['test']}: {fail['error']}")
        
        if self.warnings:
            print("\n⚠️  WARNINGS:")
            for warn in self.warnings:
                print(f"  - {warn['test']}: {warn['message']}")

results = TestResults()

def test_endpoint(name: str, method: str, endpoint: str, data: dict = None, 
                  headers: dict = None, expected_status: int = 200, 
                  should_contain: str = None) -> bool:
    """Test a single endpoint"""
    try:
        url = f"{BASE_URL}{endpoint}"
        
        if method == "GET":
            response = requests.get(url, headers=headers, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers, timeout=10)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers, timeout=10)
        else:
            results.add_fail(name, f"Unknown method: {method}")
            return False
        
        # Check status code
        if response.status_code != expected_status:
            if response.status_code == 500:
                try:
                    error_detail = response.json().get('detail', 'Unknown error')
                    results.add_fail(name, f"Status {response.status_code}: {error_detail}")
                except:
                    results.add_fail(name, f"Status {response.status_code}: {response.text[:200]}")
            else:
                results.add_fail(name, f"Expected {expected_status}, got {response.status_code}")
            return False
        
        # Check content if specified
        if should_contain:
            content = response.text
            if should_contain not in content:
                results.add_fail(name, f"Response doesn't contain '{should_contain}'")
                return False
        
        results.add_pass(name, f"Status: {response.status_code}")
        return True
        
    except requests.exceptions.Timeout:
        results.add_fail(name, "Request timeout")
        return False
    except requests.exceptions.ConnectionError:
        results.add_fail(name, "Connection error - is server running?")
        return False
    except Exception as e:
        results.add_fail(name, f"Exception: {str(e)}")
        return False

print("="*70)
print("SUPERAGENT V8 - COMPREHENSIVE TEST SUITE")
print("="*70)
print()

# Test 1: Core System Tests
print("📋 CATEGORY: Core System Tests")
print("-"*70)

test_endpoint("Health Check", "GET", "/health")
test_endpoint("Root Endpoint", "GET", "/")
test_endpoint("API Documentation", "GET", "/docs")

# Test 2: File Operations
print("\n📋 CATEGORY: File Operations")
print("-"*70)

test_endpoint("List Files", "POST", "/files/list", {"directory": ".", "recursive": False})
test_endpoint("File Search", "POST", "/files/search", {"pattern": "*.py"})

# Test 3: Project Management
print("\n📋 CATEGORY: Project Management")
print("-"*70)

test_endpoint("List Templates", "GET", "/projects/templates")
test_endpoint("Project Analysis", "GET", "/project/analyze")
test_endpoint("Project Type Detection", "GET", "/project/type")

# Test 4: Git Operations
print("\n📋 CATEGORY: Git Operations")
print("-"*70)

test_endpoint("Git Status", "GET", "/git-status")
test_endpoint("Git Status (Enhanced)", "GET", "/git/status")

# Test 5: Environment & Dependencies
print("\n📋 CATEGORY: Environment & Dependencies")
print("-"*70)

test_endpoint("List Environment Variables", "GET", "/env/list")
test_endpoint("Available Modules", "GET", "/modules/available")
test_endpoint("Installed Modules", "GET", "/modules/installed")

# Test 6: Workflows
print("\n📋 CATEGORY: Workflows")
print("-"*70)

test_endpoint("List Workflows", "GET", "/workflows/list")

# Test 7: Checkpoints & Rollback
print("\n📋 CATEGORY: Checkpoints & Rollback")
print("-"*70)

test_endpoint("List Checkpoints", "GET", "/checkpoint/list")

# Test 8: Diagnostics
print("\n📋 CATEGORY: Diagnostics")
print("-"*70)

test_endpoint("System Diagnostics", "GET", "/diagnostics/check")

# Test 9: Memory & Context
print("\n📋 CATEGORY: Memory & Context")
print("-"*70)

test_endpoint("Memory Stats", "GET", "/memory-stats")
test_endpoint("Memory Conversations", "GET", "/api/v1/memory/conversations")
test_endpoint("Memory Projects", "GET", "/api/v1/memory/projects")

# Test 10: Cache
print("\n📋 CATEGORY: Cache System")
print("-"*70)

test_endpoint("Cache Stats", "GET", "/cache-stats")

# Test 11: AI Providers
print("\n📋 CATEGORY: AI Providers")
print("-"*70)

test_endpoint("List AI Providers", "GET", "/ai/providers")

# Test 12: Security
print("\n📋 CATEGORY: Security")
print("-"*70)

test_endpoint("Cybersecurity Status", "GET", "/cybersecurity/status")

# Test 13: Plugins
print("\n📋 CATEGORY: Plugins")
print("-"*70)

test_endpoint("List Plugins", "GET", "/plugins/list")

# Test 14: Voice Interface
print("\n📋 CATEGORY: Voice Interface")
print("-"*70)

test_endpoint("Voice Stats", "GET", "/voice/stats")
test_endpoint("Available Voices", "GET", "/voice/voices")

# Test 15: Docker Sandbox
print("\n📋 CATEGORY: Docker Sandbox")
print("-"*70)

test_endpoint("Sandbox Stats", "GET", "/sandbox/stats")
test_endpoint("Sandbox Images", "GET", "/sandbox/images")

# Test 16: Code Review
print("\n📋 CATEGORY: Code Review")
print("-"*70)

test_endpoint("Review Stats", "GET", "/review/stats")

# Test 17: Codebase Intelligence
print("\n📋 CATEGORY: Codebase Intelligence")
print("-"*70)

test_endpoint("Codebase Stats", "GET", "/codebase/stats")

# Test 18: Error Prevention
print("\n📋 CATEGORY: Error Prevention")
print("-"*70)

test_endpoint("Error Stats", "GET", "/errors/stats")

# Test 19: Visual Editor
print("\n📋 CATEGORY: Visual Editor")
print("-"*70)

test_endpoint("Visual Components", "GET", "/visual-editor/components")

# Test 20: Plan Mode
print("\n📋 CATEGORY: Plan Mode")
print("-"*70)

test_endpoint("Active Plan", "GET", "/plan-mode/active")

# Test 21: Multiplayer
print("\n📋 CATEGORY: Multiplayer")
print("-"*70)

test_endpoint("List Rooms", "GET", "/multiplayer/rooms")

# Test 22: Self-Repair
print("\n📋 CATEGORY: Self-Repair System")
print("-"*70)

test_endpoint("Self-Repair Health", "GET", "/self-repair/health")
test_endpoint("Self-Repair Errors", "GET", "/self-repair/errors")
test_endpoint("Self-Repair Repairs", "GET", "/self-repair/repairs")

# Test 23: Logs
print("\n📋 CATEGORY: Logging")
print("-"*70)

test_endpoint("Recent Logs", "GET", "/logs/recent")

# Test 24: Redis Cache
print("\n📋 CATEGORY: Redis Cache")
print("-"*70)

test_endpoint("Redis Health", "GET", "/cache/redis/health")

# Test 25: Integrations
print("\n📋 CATEGORY: Integrations")
print("-"*70)

test_endpoint("List Integrations", "GET", "/integrations/list")

# Test 26: Screenshots
print("\n📋 CATEGORY: Screenshots")
print("-"*70)

test_endpoint("List Screenshots", "GET", "/screenshot/list")

# Test 27: GitHub Integration
print("\n📋 CATEGORY: GitHub Integration")
print("-"*70)

test_endpoint("GitHub Status", "GET", "/api/v1/github/status")

# Test 28: Enterprise Capabilities
print("\n📋 CATEGORY: Enterprise Features")
print("-"*70)

test_endpoint("Enterprise Capabilities", "GET", "/api/v1/enterprise/capabilities")

# Test 29: Build Endpoints (will fail without API key)
print("\n📋 CATEGORY: Build Endpoints (Expected to fail without API key)")
print("-"*70)

response = requests.post(f"{BASE_URL}/build", 
                        json={"instruction": "test", "language": "html"},
                        timeout=10)
if response.status_code == 500 and "GEMINI_API_KEY" in response.text:
    results.add_pass("Build Endpoint Error Handling", "Correctly returns API key error")
else:
    results.add_warning("Build Endpoint", f"Unexpected response: {response.status_code}")

# Test 30: POST endpoints with data
print("\n📋 CATEGORY: POST Endpoints with Data")
print("-"*70)

test_endpoint("Code Search", "POST", "/code/search", 
              {"pattern": "def", "file_types": ["py"]})

test_endpoint("Web Search", "POST", "/web/search", 
              {"query": "test"})

# Print summary
print()
results.summary()

# Save results to file
report = {
    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
    "total_tests": len(results.passed) + len(results.failed) + len(results.warnings) + len(results.skipped),
    "passed": len(results.passed),
    "failed": len(results.failed),
    "warnings": len(results.warnings),
    "skipped": len(results.skipped),
    "details": {
        "passed": results.passed,
        "failed": results.failed,
        "warnings": results.warnings,
        "skipped": results.skipped
    }
}

with open("/home/ubuntu/supermen-v8/test_results.json", "w") as f:
    json.dump(report, f, indent=2)

print("\n📄 Test results saved to: test_results.json")

# Exit with appropriate code
exit_code = 0 if len(results.failed) == 0 else 1
exit(exit_code)
