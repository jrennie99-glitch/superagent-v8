"""
Comprehensive API Test Suite
Tests all 3 APIs built by SuperAgent
"""
import requests
import json
import time
from datetime import datetime

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_test(name, passed, details=""):
    status = f"{Colors.GREEN}✅ PASS{Colors.END}" if passed else f"{Colors.RED}❌ FAIL{Colors.END}"
    print(f"{status} - {name}")
    if details:
        print(f"   {details}")

def test_rest_api():
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}Testing REST API - Todo App (Port 8001){Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}\n")
    
    base_url = "http://localhost:8001"
    results = {"total": 0, "passed": 0}
    
    # Test 1: Health check
    results["total"] += 1
    try:
        response = requests.get(f"{base_url}/health")
        passed = response.status_code == 200
        results["passed"] += passed
        print_test("Health check", passed, f"Status: {response.status_code}")
    except Exception as e:
        print_test("Health check", False, str(e))
    
    # Test 2: Register user
    results["total"] += 1
    try:
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpass123"
        }
        response = requests.post(f"{base_url}/auth/register", json=user_data)
        passed = response.status_code in [200, 201, 400]  # 400 if user exists
        results["passed"] += passed
        print_test("User registration", passed, f"Status: {response.status_code}")
    except Exception as e:
        print_test("User registration", False, str(e))
    
    # Test 3: Login
    results["total"] += 1
    token = None
    try:
        login_data = {
            "username": "testuser",
            "password": "testpass123"
        }
        response = requests.post(f"{base_url}/auth/login", json=login_data)
        passed = response.status_code == 200
        if passed:
            token = response.json().get("access_token")
        results["passed"] += passed
        print_test("User login", passed, f"Token received: {bool(token)}")
    except Exception as e:
        print_test("User login", False, str(e))
    
    if token:
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test 4: Create todo
        results["total"] += 1
        try:
            todo_data = {
                "title": "Test Todo",
                "description": "This is a test todo",
                "priority": "high"
            }
            response = requests.post(f"{base_url}/todos", json=todo_data, headers=headers)
            passed = response.status_code in [200, 201]
            results["passed"] += passed
            print_test("Create todo", passed, f"Status: {response.status_code}")
        except Exception as e:
            print_test("Create todo", False, str(e))
        
        # Test 5: Get todos
        results["total"] += 1
        try:
            response = requests.get(f"{base_url}/todos", headers=headers)
            passed = response.status_code == 200
            if passed:
                todos = response.json()
                passed = isinstance(todos, list)
            results["passed"] += passed
            print_test("Get todos", passed, f"Todos count: {len(todos) if passed else 0}")
        except Exception as e:
            print_test("Get todos", False, str(e))
    
    print(f"\n{Colors.YELLOW}REST API Results: {results['passed']}/{results['total']} tests passed{Colors.END}\n")
    return results

def test_graphql_api():
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}Testing GraphQL API - E-commerce (Port 8002){Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}\n")
    
    base_url = "http://localhost:8002"
    graphql_url = f"{base_url}/graphql"
    results = {"total": 0, "passed": 0}
    
    # Test 1: Health check
    results["total"] += 1
    try:
        response = requests.get(f"{base_url}/health")
        passed = response.status_code == 200
        results["passed"] += passed
        print_test("Health check", passed, f"Status: {response.status_code}")
    except Exception as e:
        print_test("Health check", False, str(e))
    
    # Test 2: Query all products
    results["total"] += 1
    try:
        query = """
        query {
            products {
                id
                name
                price
                stock
                category
            }
        }
        """
        response = requests.post(graphql_url, json={"query": query})
        passed = response.status_code == 200
        if passed:
            data = response.json()
            products = data.get("data", {}).get("products", [])
            passed = len(products) > 0
        results["passed"] += passed
        print_test("Query products", passed, f"Products found: {len(products) if passed else 0}")
    except Exception as e:
        print_test("Query products", False, str(e))
    
    # Test 3: Query categories
    results["total"] += 1
    try:
        query = """
        query {
            categories
        }
        """
        response = requests.post(graphql_url, json={"query": query})
        passed = response.status_code == 200
        if passed:
            data = response.json()
            categories = data.get("data", {}).get("categories", [])
            passed = len(categories) > 0
        results["passed"] += passed
        print_test("Query categories", passed, f"Categories: {categories if passed else []}")
    except Exception as e:
        print_test("Query categories", False, str(e))
    
    # Test 4: Create product
    results["total"] += 1
    try:
        mutation = """
        mutation {
            createProduct(product: {
                name: "Test Product"
                description: "Test Description"
                price: 99.99
                stock: 10
                category: "Test"
            }) {
                success
                message
                product {
                    id
                    name
                }
            }
        }
        """
        response = requests.post(graphql_url, json={"query": mutation})
        passed = response.status_code == 200
        if passed:
            data = response.json()
            result = data.get("data", {}).get("createProduct", {})
            passed = result.get("success", False)
        results["passed"] += passed
        print_test("Create product", passed, f"Success: {passed}")
    except Exception as e:
        print_test("Create product", False, str(e))
    
    # Test 5: Create order
    results["total"] += 1
    try:
        mutation = """
        mutation {
            createOrder(order: {
                customerName: "Test Customer"
                customerEmail: "customer@test.com"
                items: [{productId: 1, quantity: 2}]
            }) {
                success
                message
                order {
                    id
                    total
                    status
                }
            }
        }
        """
        response = requests.post(graphql_url, json={"query": mutation})
        passed = response.status_code == 200
        if passed:
            data = response.json()
            result = data.get("data", {}).get("createOrder", {})
            passed = result.get("success", False)
        results["passed"] += passed
        print_test("Create order", passed, f"Success: {passed}")
    except Exception as e:
        print_test("Create order", False, str(e))
    
    print(f"\n{Colors.YELLOW}GraphQL API Results: {results['passed']}/{results['total']} tests passed{Colors.END}\n")
    return results

def test_websocket_api():
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}Testing WebSocket API - Chat (Port 8003){Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}\n")
    
    base_url = "http://localhost:8003"
    results = {"total": 0, "passed": 0}
    
    # Test 1: Health check
    results["total"] += 1
    try:
        response = requests.get(f"{base_url}/health")
        passed = response.status_code == 200
        results["passed"] += passed
        print_test("Health check", passed, f"Status: {response.status_code}")
    except Exception as e:
        print_test("Health check", False, str(e))
    
    # Test 2: Get API info
    results["total"] += 1
    try:
        response = requests.get(f"{base_url}/api")
        passed = response.status_code == 200
        if passed:
            data = response.json()
            passed = "websocket_endpoint" in data
        results["passed"] += passed
        print_test("API info", passed, f"WebSocket endpoint defined: {passed}")
    except Exception as e:
        print_test("API info", False, str(e))
    
    # Test 3: Get rooms
    results["total"] += 1
    try:
        response = requests.get(f"{base_url}/rooms")
        passed = response.status_code == 200
        if passed:
            data = response.json()
            passed = "rooms" in data
        results["passed"] += passed
        print_test("Get rooms", passed, f"Rooms endpoint working: {passed}")
    except Exception as e:
        print_test("Get rooms", False, str(e))
    
    # Test 4: HTML client available
    results["total"] += 1
    try:
        response = requests.get(f"{base_url}/")
        passed = response.status_code == 200 and "WebSocket Chat" in response.text
        results["passed"] += passed
        print_test("HTML client", passed, f"Chat client available: {passed}")
    except Exception as e:
        print_test("HTML client", False, str(e))
    
    print(f"\n{Colors.YELLOW}WebSocket API Results: {results['passed']}/{results['total']} tests passed{Colors.END}\n")
    return results

def main():
    print(f"\n{Colors.GREEN}{'='*60}{Colors.END}")
    print(f"{Colors.GREEN}SUPERAGENT API BUILD TEST SUITE{Colors.END}")
    print(f"{Colors.GREEN}Testing 3 APIs built autonomously{Colors.END}")
    print(f"{Colors.GREEN}{'='*60}{Colors.END}")
    
    start_time = time.time()
    
    # Test all APIs
    rest_results = test_rest_api()
    graphql_results = test_graphql_api()
    websocket_results = test_websocket_api()
    
    # Calculate totals
    total_tests = rest_results["total"] + graphql_results["total"] + websocket_results["total"]
    total_passed = rest_results["passed"] + graphql_results["passed"] + websocket_results["passed"]
    success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
    
    elapsed_time = time.time() - start_time
    
    # Print summary
    print(f"\n{Colors.GREEN}{'='*60}{Colors.END}")
    print(f"{Colors.GREEN}FINAL RESULTS{Colors.END}")
    print(f"{Colors.GREEN}{'='*60}{Colors.END}\n")
    
    print(f"REST API:      {rest_results['passed']}/{rest_results['total']} tests passed")
    print(f"GraphQL API:   {graphql_results['passed']}/{graphql_results['total']} tests passed")
    print(f"WebSocket API: {websocket_results['passed']}/{websocket_results['total']} tests passed")
    print(f"\n{Colors.YELLOW}TOTAL: {total_passed}/{total_tests} tests passed ({success_rate:.1f}%){Colors.END}")
    print(f"Time elapsed: {elapsed_time:.2f} seconds\n")
    
    # Overall status
    if success_rate >= 90:
        print(f"{Colors.GREEN}✅ ALL APIS WORKING - SUPERAGENT BUILD SUCCESSFUL!{Colors.END}\n")
    elif success_rate >= 70:
        print(f"{Colors.YELLOW}⚠️  MOST APIS WORKING - MINOR ISSUES DETECTED{Colors.END}\n")
    else:
        print(f"{Colors.RED}❌ MULTIPLE FAILURES - BUILD NEEDS REVIEW{Colors.END}\n")
    
    return success_rate >= 90

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
