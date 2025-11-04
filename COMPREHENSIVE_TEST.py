#!/usr/bin/env python3
"""
Comprehensive SuperAgent Test Suite
Tests everything before Koyeb deployment
"""

import os
import sys
from pathlib import Path
import ast
import subprocess

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text:^80}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.RESET}\n")

def print_success(text):
    print(f"{Colors.GREEN}✓ {text}{Colors.RESET}")

def print_error(text):
    print(f"{Colors.RED}✗ {text}{Colors.RESET}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠ {text}{Colors.RESET}")

def print_info(text):
    print(f"{Colors.BLUE}ℹ {text}{Colors.RESET}")

# Test results tracking
tests_passed = 0
tests_failed = 0
warnings = []
errors = []

def test_file_structure():
    """Test 1: Verify all critical files exist"""
    print_header("TEST 1: FILE STRUCTURE")
    global tests_passed, tests_failed
    
    required_files = [
        "index.html",
        "pricing.html",
        "Dockerfile",
        ".dockerignore",
        "requirements-deploy.txt",
        "superagent/api.py",
        "superagent/core/agent.py",
        "superagent/core/multi_agent.py",
        "superagent/core/config.py",
        "config.yaml"
    ]
    
    for file_path in required_files:
        path = Path(file_path)
        if path.exists():
            print_success(f"{file_path} exists")
            tests_passed += 1
        else:
            print_error(f"{file_path} MISSING!")
            tests_failed += 1
            errors.append(f"Missing: {file_path}")

def test_python_syntax():
    """Test 2: Check Python files for syntax errors"""
    print_header("TEST 2: PYTHON SYNTAX")
    global tests_passed, tests_failed
    
    python_files = [
        "superagent/api.py",
        "superagent/core/agent.py",
        "superagent/core/multi_agent.py",
        "superagent/core/config.py"
    ]
    
    for py_file in python_files:
        path = Path(py_file)
        if not path.exists():
            continue
            
        try:
            with open(path, 'r') as f:
                code = f.read()
                ast.parse(code)
            print_success(f"{py_file} - Valid Python syntax")
            tests_passed += 1
        except SyntaxError as e:
            print_error(f"{py_file} - Syntax error: {e}")
            tests_failed += 1
            errors.append(f"Syntax error in {py_file}: {e}")

def test_html_files():
    """Test 3: Check HTML files are valid"""
    print_header("TEST 3: HTML FILES")
    global tests_passed, tests_failed
    
    html_files = ["index.html", "pricing.html"]
    
    for html_file in html_files:
        path = Path(html_file)
        if not path.exists():
            continue
            
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Check for basic HTML structure
            if '<!DOCTYPE html>' in content and '<html' in content and '</html>' in content:
                print_success(f"{html_file} - Valid HTML structure")
                tests_passed += 1
            else:
                print_error(f"{html_file} - Invalid HTML structure")
                tests_failed += 1
                errors.append(f"Invalid HTML: {html_file}")
                
            # Check file size
            size_kb = len(content) / 1024
            print_info(f"  Size: {size_kb:.2f} KB")
            
        except Exception as e:
            print_error(f"{html_file} - Error reading: {e}")
            tests_failed += 1
            errors.append(f"Error reading {html_file}: {e}")

def test_docker_config():
    """Test 4: Verify Docker configuration"""
    print_header("TEST 4: DOCKER CONFIGURATION")
    global tests_passed, tests_failed
    
    # Check Dockerfile
    dockerfile = Path("Dockerfile")
    if dockerfile.exists():
        with open(dockerfile, 'r') as f:
            content = f.read()
            
        checks = [
            ("FROM python:3.11", "Base image specified"),
            ("COPY requirements-deploy.txt", "Deployment requirements copied"),
            ("RUN pip install", "Dependencies installed"),
            ("COPY . .", "Application code copied"),
            ("EXPOSE 8000", "Port exposed"),
            ("CMD", "Start command defined")
        ]
        
        for check_str, description in checks:
            if check_str in content:
                print_success(f"Dockerfile: {description}")
                tests_passed += 1
            else:
                print_warning(f"Dockerfile: {description} - NOT FOUND")
                warnings.append(f"Dockerfile missing: {description}")
                
    # Check .dockerignore
    dockerignore = Path(".dockerignore")
    if dockerignore.exists():
        with open(dockerignore, 'r') as f:
            content = f.read()
            
        # Make sure HTML files are NOT ignored
        if 'index.html' not in content and 'pricing.html' not in content:
            print_success(".dockerignore: HTML files will be included")
            tests_passed += 1
        else:
            print_error(".dockerignore: HTML files are excluded!")
            tests_failed += 1
            errors.append("HTML files excluded in .dockerignore")

def test_requirements():
    """Test 5: Check requirements files"""
    print_header("TEST 5: REQUIREMENTS FILES")
    global tests_passed, tests_failed
    
    req_file = Path("requirements-deploy.txt")
    if req_file.exists():
        with open(req_file, 'r') as f:
            packages = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            
        essential_packages = [
            'fastapi',
            'uvicorn',
            'groq',
            'structlog',
            'pydantic'
        ]
        
        for package in essential_packages:
            found = any(package in line.lower() for line in packages)
            if found:
                print_success(f"Package found: {package}")
                tests_passed += 1
            else:
                print_error(f"Package missing: {package}")
                tests_failed += 1
                errors.append(f"Missing package: {package}")
                
        print_info(f"  Total packages: {len(packages)}")

def test_api_structure():
    """Test 6: Check API structure"""
    print_header("TEST 6: API STRUCTURE")
    global tests_passed, tests_failed
    
    api_file = Path("superagent/api.py")
    if api_file.exists():
        with open(api_file, 'r') as f:
            content = f.read()
            
        endpoints = [
            ("@app.get(\"/\"", "Root endpoint (serves HTML)"),
            ("@app.get(\"/health\"", "Health check endpoint"),
            ("@app.post(\"/execute\"", "Execute endpoint"),
            ("@app.post(\"/generate\"", "Generate endpoint"),
            ("@app.get(\"/jobs", "Jobs endpoint"),
            ("HTMLResponse", "HTML response import")
        ]
        
        for check_str, description in endpoints:
            if check_str in content:
                print_success(f"API: {description}")
                tests_passed += 1
            else:
                print_warning(f"API: {description} - NOT FOUND")
                warnings.append(f"API missing: {description}")

def test_supervisors():
    """Test 7: Check 2-Supervisor + Supreme Agent system"""
    print_header("TEST 7: SUPERVISOR SYSTEM")
    global tests_passed, tests_failed
    
    multi_agent = Path("superagent/core/multi_agent.py")
    if multi_agent.exists():
        with open(multi_agent, 'r') as f:
            content = f.read()
            
        checks = [
            ("class SupervisorSystem", "SupervisorSystem class exists"),
            ("SUPERVISOR", "Supervisor role defined"),
            ("SUPREME_AGENT", "Supreme Agent role defined"),
            ("for i in range(2)", "2 Supervisors created"),
            ("asyncio.gather", "Parallel execution"),
            ("2/2", "2/2 consensus logic")
        ]
        
        for check_str, description in checks:
            if check_str in content:
                print_success(f"Supervisors: {description}")
                tests_passed += 1
            else:
                print_error(f"Supervisors: {description} - NOT FOUND")
                tests_failed += 1
                errors.append(f"Supervisor system missing: {description}")

def test_frontend_backend_connection():
    """Test 8: Check frontend connects to backend"""
    print_header("TEST 8: FRONTEND-BACKEND CONNECTION")
    global tests_passed, tests_failed
    
    index_html = Path("index.html")
    if index_html.exists():
        with open(index_html, 'r', encoding='utf-8') as f:
            content = f.read()
            
        checks = [
            ("fetch('/execute'", "Frontend calls /execute endpoint"),
            ("fetch(`/jobs/", "Frontend polls job status"),
            ("X-API-Key", "API key authentication"),
            ("Planning project architecture", "Shows supervisor steps"),
            ("Supreme Agent final review", "Shows supreme agent step"),
            ("pollJobStatus", "Job polling function")
        ]
        
        for check_str, description in checks:
            if check_str in content:
                print_success(f"Frontend: {description}")
                tests_passed += 1
            else:
                print_error(f"Frontend: {description} - NOT FOUND")
                tests_failed += 1
                errors.append(f"Frontend missing: {description}")

def test_environment_requirements():
    """Test 9: Check environment variable references"""
    print_header("TEST 9: ENVIRONMENT VARIABLES")
    global tests_passed, tests_failed
    
    api_file = Path("superagent/api.py")
    if api_file.exists():
        with open(api_file, 'r') as f:
            content = f.read()
            
        env_vars = [
            ("GROQ_API_KEY", "Groq API key"),
            ("SUPERAGENT_API_KEY", "SuperAgent API key")
        ]
        
        for var_name, description in env_vars:
            if var_name in content:
                print_success(f"ENV: {description} referenced")
                tests_passed += 1
            else:
                print_warning(f"ENV: {description} - NOT FOUND")
                warnings.append(f"Environment variable not referenced: {var_name}")

def print_summary():
    """Print final test summary"""
    print_header("TEST SUMMARY")
    
    total_tests = tests_passed + tests_failed
    pass_rate = (tests_passed / total_tests * 100) if total_tests > 0 else 0
    
    print(f"\n{Colors.BOLD}Total Tests: {total_tests}{Colors.RESET}")
    print(f"{Colors.GREEN}Passed: {tests_passed}{Colors.RESET}")
    print(f"{Colors.RED}Failed: {tests_failed}{Colors.RESET}")
    print(f"{Colors.YELLOW}Warnings: {len(warnings)}{Colors.RESET}")
    print(f"\n{Colors.BOLD}Pass Rate: {pass_rate:.1f}%{Colors.RESET}\n")
    
    if errors:
        print(f"\n{Colors.RED}{Colors.BOLD}CRITICAL ERRORS:{Colors.RESET}")
        for error in errors:
            print(f"{Colors.RED}  • {error}{Colors.RESET}")
    
    if warnings:
        print(f"\n{Colors.YELLOW}{Colors.BOLD}WARNINGS:{Colors.RESET}")
        for warning in warnings:
            print(f"{Colors.YELLOW}  • {warning}{Colors.RESET}")
    
    print()
    
    if tests_failed == 0 and len(errors) == 0:
        print(f"{Colors.GREEN}{Colors.BOLD}{'='*80}{Colors.RESET}")
        print(f"{Colors.GREEN}{Colors.BOLD}🎉 ALL TESTS PASSED! READY FOR DEPLOYMENT! 🎉{Colors.RESET}")
        print(f"{Colors.GREEN}{Colors.BOLD}{'='*80}{Colors.RESET}\n")
        return 0
    else:
        print(f"{Colors.RED}{Colors.BOLD}{'='*80}{Colors.RESET}")
        print(f"{Colors.RED}{Colors.BOLD}❌ TESTS FAILED! FIX ERRORS BEFORE DEPLOYING! ❌{Colors.RESET}")
        print(f"{Colors.RED}{Colors.BOLD}{'='*80}{Colors.RESET}\n")
        return 1

def main():
    print_header("SUPERAGENT COMPREHENSIVE TEST SUITE")
    print_info("Testing all components before Koyeb deployment...\n")
    
    # Run all tests
    test_file_structure()
    test_python_syntax()
    test_html_files()
    test_docker_config()
    test_requirements()
    test_api_structure()
    test_supervisors()
    test_frontend_backend_connection()
    test_environment_requirements()
    
    # Print summary
    return print_summary()

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

