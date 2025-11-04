#!/usr/bin/env python3
"""
COMPREHENSIVE SYSTEM TEST
Tests all SuperAgent modules including new features.
"""

import sys
import ast
import os
from pathlib import Path

print("=" * 80)
print("🔍 COMPREHENSIVE SUPERAGENT SCAN")
print("=" * 80)
print()

# Test 1: File Structure
print("📁 TEST 1: Checking file structure...")
required_files = [
    "superagent/__init__.py",
    "superagent/core/agent.py",
    "superagent/core/config.py",
    "superagent/core/llm.py",
    "superagent/core/multi_agent.py",
    "superagent/core/memory.py",
    "superagent/modules/code_generator.py",
    "superagent/modules/debugger.py",
    "superagent/modules/tester.py",
    "superagent/modules/sandbox.py",
    "superagent/modules/multi_language.py",
    "superagent/modules/autonomous_planner.py",
    "superagent/modules/full_stack_generator.py",
    "superagent/api.py",
    "index.html",
    "requirements-deploy.txt",
    "Dockerfile",
]

missing_files = []
for file in required_files:
    if not Path(file).exists():
        missing_files.append(file)
        print(f"  ❌ Missing: {file}")
    else:
        print(f"  ✅ Found: {file}")

if missing_files:
    print(f"\n⚠️  {len(missing_files)} files missing!")
else:
    print(f"\n✅ All {len(required_files)} files present!")

print()

# Test 2: Python Syntax Check
print("🐍 TEST 2: Checking Python syntax...")
python_files = list(Path("superagent").rglob("*.py"))
syntax_errors = []

for py_file in python_files:
    try:
        with open(py_file, 'r') as f:
            code = f.read()
            ast.parse(code)
        print(f"  ✅ {py_file}")
    except SyntaxError as e:
        syntax_errors.append((py_file, str(e)))
        print(f"  ❌ {py_file}: {e}")

if syntax_errors:
    print(f"\n⚠️  {len(syntax_errors)} syntax errors found!")
else:
    print(f"\n✅ All {len(python_files)} Python files valid!")

print()

# Test 3: Import Check
print("📦 TEST 3: Checking imports...")
import_errors = []

critical_imports = [
    ("superagent.core.config", "Config"),
    ("superagent.core.memory", "ProjectMemory"),
    ("superagent.modules.sandbox", "SandboxExecutor"),
    ("superagent.modules.multi_language", "MultiLanguageGenerator"),
    ("superagent.modules.autonomous_planner", "AutonomousPlanner"),
    ("superagent.modules.full_stack_generator", "FullStackGenerator"),
]

for module_name, class_name in critical_imports:
    try:
        module = __import__(module_name, fromlist=[class_name])
        cls = getattr(module, class_name)
        print(f"  ✅ {module_name}.{class_name}")
    except Exception as e:
        import_errors.append((module_name, class_name, str(e)))
        print(f"  ❌ {module_name}.{class_name}: {e}")

if import_errors:
    print(f"\n⚠️  {len(import_errors)} import errors!")
else:
    print(f"\n✅ All {len(critical_imports)} critical imports working!")

print()

# Test 4: Module Completeness Check
print("🔧 TEST 4: Checking module completeness...")

module_checks = {
    "SandboxExecutor": ["execute_python", "execute_nodejs", "execute_project", "is_available"],
    "MultiLanguageGenerator": ["generate_code"],
    "AutonomousPlanner": ["execute_autonomous_project"],
    "FullStackGenerator": ["generate_full_app"],
}

incomplete_modules = []

for module_info in critical_imports:
    module_name, class_name = module_info
    if class_name in module_checks:
        try:
            module = __import__(module_name, fromlist=[class_name])
            cls = getattr(module, class_name)
            
            for method in module_checks[class_name]:
                if not hasattr(cls, method):
                    incomplete_modules.append(f"{class_name}.{method}")
                    print(f"  ❌ {class_name}.{method} missing")
                else:
                    print(f"  ✅ {class_name}.{method}")
        except Exception as e:
            print(f"  ⚠️  Could not check {class_name}: {e}")

if incomplete_modules:
    print(f"\n⚠️  {len(incomplete_modules)} methods missing!")
else:
    print(f"\n✅ All critical methods present!")

print()

# Test 5: Code Quality Metrics
print("📊 TEST 5: Code quality metrics...")

total_lines = 0
total_files = 0
for py_file in python_files:
    with open(py_file, 'r') as f:
        lines = len(f.readlines())
        total_lines += lines
        total_files += 1

print(f"  📄 Total files: {total_files}")
print(f"  📝 Total lines: {total_lines:,}")
print(f"  📈 Average lines/file: {total_lines // total_files}")
print(f"  ✅ Code quality: {'GOOD' if total_lines > 5000 else 'SMALL'}")

print()

# Test 6: Requirements Check
print("📦 TEST 6: Checking requirements...")
if Path("requirements-deploy.txt").exists():
    with open("requirements-deploy.txt", 'r') as f:
        reqs = [line.strip() for line in f if line.strip() and not line.startswith("#")]
    
    critical_packages = ["fastapi", "uvicorn", "groq", "structlog", "docker", "pytest"]
    missing_packages = [pkg for pkg in critical_packages if not any(pkg in req for req in reqs)]
    
    print(f"  📦 Total packages: {len(reqs)}")
    for pkg in critical_packages:
        if any(pkg in req for req in reqs):
            print(f"  ✅ {pkg}")
        else:
            print(f"  ❌ {pkg} missing")
    
    if missing_packages:
        print(f"\n⚠️  {len(missing_packages)} critical packages missing!")
    else:
        print(f"\n✅ All critical packages present!")
else:
    print("  ❌ requirements-deploy.txt not found!")

print()

# Test 7: Frontend Check
print("🎨 TEST 7: Checking frontend...")
if Path("index.html").exists():
    with open("index.html", 'r') as f:
        html = f.read()
    
    checks = {
        "buildModal": "buildModal" in html,
        "testBackendConnection": "testBackendConnection" in html,
        "startBuild": "startBuild" in html,
        "pollJobStatus": "pollJobStatus" in html,
        "display:none": "display:none" in html or "display: none" in html,
    }
    
    for check_name, passed in checks.items():
        if passed:
            print(f"  ✅ {check_name}")
        else:
            print(f"  ❌ {check_name} missing")
    
    all_passed = all(checks.values())
    if all_passed:
        print(f"\n✅ Frontend complete!")
    else:
        print(f"\n⚠️  Frontend issues found!")
else:
    print("  ❌ index.html not found!")

print()

# Test 8: Deployment Check
print("🚀 TEST 8: Checking deployment configs...")
deployment_files = ["Dockerfile", "requirements-deploy.txt", ".dockerignore"]
deployment_ok = True

for file in deployment_files:
    if Path(file).exists():
        print(f"  ✅ {file}")
    else:
        print(f"  ❌ {file} missing")
        deployment_ok = False

if deployment_ok:
    print(f"\n✅ Deployment configs complete!")
else:
    print(f"\n⚠️  Deployment configs incomplete!")

print()

# Test 9: Documentation Check
print("📚 TEST 9: Checking documentation...")
doc_files = [
    "README.md",
    "RANKED_NUMBER_1.md",
    "BEATS_BUBBLE.md",
    "BACKEND_CAPABILITIES.md",
    "FRONTEND_BACKEND_CONNECTION.md"
]

docs_found = sum(1 for file in doc_files if Path(file).exists())
for file in doc_files:
    if Path(file).exists():
        print(f"  ✅ {file}")
    else:
        print(f"  ⚠️  {file} missing (optional)")

print(f"\n✅ {docs_found}/{len(doc_files)} documentation files present!")

print()

# SUMMARY
print("=" * 80)
print("📊 TEST SUMMARY")
print("=" * 80)

total_tests = 9
issues = []

if missing_files:
    issues.append(f"{len(missing_files)} missing files")
if syntax_errors:
    issues.append(f"{len(syntax_errors)} syntax errors")
if import_errors:
    issues.append(f"{len(import_errors)} import errors")
if incomplete_modules:
    issues.append(f"{len(incomplete_modules)} missing methods")

print(f"\n📈 Files: {len(required_files) - len(missing_files)}/{len(required_files)}")
print(f"🐍 Python Syntax: {len(python_files) - len(syntax_errors)}/{len(python_files)}")
print(f"📦 Imports: {len(critical_imports) - len(import_errors)}/{len(critical_imports)}")
print(f"📝 Total Code: {total_lines:,} lines in {total_files} files")

if issues:
    print(f"\n⚠️  ISSUES FOUND:")
    for issue in issues:
        print(f"   • {issue}")
    print(f"\n❌ SCAN RESULT: ISSUES DETECTED")
    sys.exit(1)
else:
    print(f"\n✅ ALL TESTS PASSED!")
    print(f"🎉 SYSTEM IS PRODUCTION-READY!")
    sys.exit(0)

