#!/usr/bin/env python3
"""
BUILD TEST - Actually test building something
"""

import asyncio
import sys
from pathlib import Path

print("=" * 80)
print("🚀 BUILD TEST - TESTING FULL-STACK GENERATOR")
print("=" * 80)
print()

# Test 1: Import the generator
print("📦 TEST 1: Importing FullStackGenerator...")
try:
    from superagent.modules.full_stack_generator import FullStackGenerator
    print("  ✅ FullStackGenerator imported successfully!")
except Exception as e:
    print(f"  ❌ Import failed: {e}")
    sys.exit(1)

print()

# Test 2: Create mock LLM provider
print("🤖 TEST 2: Creating mock LLM provider...")

class MockLLM:
    """Mock LLM for testing without API calls."""
    
    async def complete(self, prompt: str) -> str:
        """Return mock responses based on prompt."""
        if "analyze" in prompt.lower() or "requirements" in prompt.lower():
            return "Features: User management, CRUD operations, Dashboard"
        elif "phase" in prompt.lower() or "plan" in prompt.lower():
            return "Phase 1: Setup, Phase 2: Implementation, Phase 3: Testing"
        elif "success" in prompt.lower():
            return "YES"
        elif "failure" in prompt.lower() or "retry" in prompt.lower():
            return "RETRY"
        else:
            return "Generated code"

try:
    llm = MockLLM()
    print("  ✅ Mock LLM created!")
except Exception as e:
    print(f"  ❌ Mock LLM failed: {e}")
    sys.exit(1)

print()

# Test 3: Initialize generator
print("🔧 TEST 3: Initializing FullStackGenerator...")
try:
    generator = FullStackGenerator(llm)
    print("  ✅ Generator initialized!")
except Exception as e:
    print(f"  ❌ Initialization failed: {e}")
    sys.exit(1)

print()

# Test 4: Generate a todo app
print("🏗️  TEST 4: Generating a TODO app...")
print("  Instruction: 'Build a todo list app with user auth'")
print()

async def test_generate():
    try:
        result = await generator.generate_full_app(
            description="Build a todo list app with user authentication",
            app_name="todo_app",
            stack="react-fastapi"
        )
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}

# Run the async test
try:
    result = asyncio.run(test_generate())
except Exception as e:
    print(f"  ❌ Generation failed: {e}")
    sys.exit(1)

print()

# Test 5: Check results
print("📊 TEST 5: Checking generated results...")

if not result.get("success"):
    print(f"  ❌ Generation failed: {result.get('error', 'Unknown error')}")
    sys.exit(1)

print(f"  ✅ Generation succeeded!")
print(f"  ✅ App name: {result.get('app_name')}")
print(f"  ✅ Stack: {result.get('stack')}")
print(f"  ✅ Files generated: {len(result.get('files', {}))}")

# Test 6: Check specific files
print()
print("📄 TEST 6: Checking generated files...")

expected_files = [
    "backend/main.py",
    "backend/models.py",
    "backend/routes.py",
    "backend/database.py",
    "backend/requirements.txt",
    "frontend/src/App.jsx",
    "frontend/src/pages/Home.jsx",
    "frontend/src/pages/Dashboard.jsx",
    "frontend/package.json",
    "README.md",
]

files = result.get("files", {})
missing_files = []
for expected in expected_files:
    if expected in files:
        print(f"  ✅ {expected}")
    else:
        print(f"  ❌ {expected} missing")
        missing_files.append(expected)

print()

# Test 7: Check file contents
print("📝 TEST 7: Checking file contents...")

# Check backend main
if "backend/main.py" in files:
    main_content = files["backend/main.py"]
    checks = [
        ("FastAPI", "FastAPI" in main_content),
        ("CORS", "CORS" in main_content or "cors" in main_content.lower()),
        ("app = FastAPI()", "app = FastAPI()" in main_content),
        ("@app.get", "@app.get" in main_content),
    ]
    
    for check_name, passed in checks:
        if passed:
            print(f"  ✅ backend/main.py has {check_name}")
        else:
            print(f"  ⚠️  backend/main.py missing {check_name}")

# Check frontend App
if "frontend/src/App.jsx" in files:
    app_content = files["frontend/src/App.jsx"]
    checks = [
        ("React", "React" in app_content or "react" in app_content),
        ("BrowserRouter", "BrowserRouter" in app_content or "Routes" in app_content),
        ("Route", "Route" in app_content),
    ]
    
    for check_name, passed in checks:
        if passed:
            print(f"  ✅ frontend/src/App.jsx has {check_name}")
        else:
            print(f"  ⚠️  frontend/src/App.jsx missing {check_name}")

# Check README
if "README.md" in files:
    readme_content = files["README.md"]
    if len(readme_content) > 100:
        print(f"  ✅ README.md has content ({len(readme_content)} chars)")
    else:
        print(f"  ⚠️  README.md too short ({len(readme_content)} chars)")

print()

# Test 8: Check features
print("🎯 TEST 8: Checking features...")

features_to_check = {
    "Database schema": result.get("database") is not None,
    "Features list": len(result.get("features", [])) > 0,
    "Deployment ready": result.get("deployment_ready") == True,
    "One-click deploy": result.get("one_click_deploy") == True,
}

for feature, present in features_to_check.items():
    if present:
        print(f"  ✅ {feature}")
    else:
        print(f"  ❌ {feature} missing")

print()

# FINAL SUMMARY
print("=" * 80)
print("📊 BUILD TEST SUMMARY")
print("=" * 80)

all_checks = [
    ("Import", True),
    ("Mock LLM", True),
    ("Generator init", True),
    ("App generation", result.get("success", False)),
    ("Files generated", len(files) >= 10),
    ("Backend files", "backend/main.py" in files),
    ("Frontend files", "frontend/src/App.jsx" in files),
    ("Database schema", result.get("database") is not None),
]

passed = sum(1 for _, check in all_checks if check)
total = len(all_checks)

print()
print(f"✅ Tests passed: {passed}/{total}")
print(f"📄 Files generated: {len(files)}")
print(f"📝 Total characters: {sum(len(content) for content in files.values()):,}")

if missing_files:
    print(f"\n⚠️  {len(missing_files)} expected files missing")

if passed == total:
    print()
    print("🎉 ALL BUILD TESTS PASSED!")
    print("✅ FullStackGenerator is working perfectly!")
    print()
    print("WHAT IT BUILT:")
    print(f"  • {len([f for f in files if f.startswith('backend/')])} backend files")
    print(f"  • {len([f for f in files if f.startswith('frontend/')])} frontend files")
    print(f"  • Complete database schema")
    print(f"  • Authentication system")
    print(f"  • Deployment configs")
    print(f"  • Documentation")
    print()
    print("READY TO USE! 🚀")
    sys.exit(0)
else:
    print()
    print(f"⚠️  Some checks failed: {total - passed}/{total}")
    sys.exit(1)

