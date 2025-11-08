"""
E2E Test Runner - Automated Feature Verification System
Validates that generated apps actually work by testing in real browsers
"""

import asyncio
import logging
from typing import Dict, List, Optional
from pathlib import Path
from playwright.async_api import async_playwright, Browser, Page, TimeoutError as PlaywrightTimeout
import http.server
import socketserver
import threading
import time
import re

logger = logging.getLogger(__name__)


class E2ETestRunner:
    """Automated E2E testing system for generated applications"""
    
    def __init__(self):
        self.browser: Optional[Browser] = None
        self.server_thread: Optional[threading.Thread] = None
        self.server: Optional[socketserver.TCPServer] = None
        self.test_port = 8765
    
    async def verify_app_features(
        self, 
        app_path: Path, 
        app_type: str,
        required_features: List[str]
    ) -> Dict:
        """
        Main entry point - verify all features work in the generated app
        
        Args:
            app_path: Path to the generated app directory
            app_type: Type of app (calculator, todo, dashboard, etc.)
            required_features: List of features that should be working
            
        Returns:
            Dict with test results, passed/failed features, critical issues
        """
        try:
            logger.info(f"🧪 Starting E2E verification for {app_type}")
            
            # Start local web server to serve the app
            await self._start_local_server(app_path)
            
            # Launch browser
            async with async_playwright() as p:
                self.browser = await p.chromium.launch(headless=True)
                context = await self.browser.new_context(viewport={'width': 1920, 'height': 1080})
                page = await context.new_page()
                
                # Navigate to app
                url = f"http://localhost:{self.test_port}/index.html"
                await page.goto(url, wait_until='networkidle')
                
                # Run type-specific tests
                if "calculator" in app_type.lower():
                    results = await self._test_calculator(page, required_features)
                elif "todo" in app_type.lower() or "task" in app_type.lower():
                    results = await self._test_todo_app(page, required_features)
                elif "dashboard" in app_type.lower():
                    results = await self._test_dashboard(page, required_features)
                elif "game" in app_type.lower():
                    results = await self._test_game(page, required_features)
                else:
                    results = await self._test_generic_app(page, required_features)
                
                await context.close()
                await self.browser.close()
            
            # Stop server
            self._stop_local_server()
            
            logger.info(f"✅ E2E testing complete - {results['passed']}/{results['total']} tests passed")
            return results
            
        except Exception as e:
            logger.error(f"❌ E2E testing failed: {str(e)}")
            self._stop_local_server()
            return {
                "success": False,
                "error": str(e),
                "passed": 0,
                "failed": 0,
                "total": 0,
                "critical_issues": [f"E2E test runner failed: {str(e)}"]
            }
    
    async def _test_calculator(self, page: Page, features: List[str]) -> Dict:
        """Test calculator-specific features"""
        passed_tests = []
        failed_tests = []
        critical_issues = []
        
        try:
            # Test 1: Basic arithmetic
            await page.click('text=7')
            await page.click('text=+')
            await page.click('text=3')
            await page.click('text==')
            display = await page.locator('input[type="text"], .display, #display').first.input_value()
            if '10' in display:
                passed_tests.append("Basic arithmetic (7+3=10)")
            else:
                failed_tests.append(f"Basic arithmetic failed - got '{display}' instead of 10")
                critical_issues.append("Basic arithmetic is broken")
            
            # Test 2: Operator precedence (2+3×4 should = 14, not 20)
            await page.click('text=C')
            await page.click('text=2')
            await page.click('text=+')
            await page.click('text=3')
            await page.click('text=×')
            await page.click('text=4')
            await page.click('text==')
            display = await page.locator('input[type="text"], .display, #display').first.input_value()
            if '14' in display:
                passed_tests.append("Operator precedence (2+3×4=14) ✅ EXPRESSION PARSER WORKING")
            else:
                failed_tests.append(f"Operator precedence BROKEN - got '{display}' instead of 14")
                critical_issues.append("❌ CRITICAL: No expression parser - calculates sequentially like basic calculator")
            
            # Test 3: Scientific functions (if mentioned)
            if any(keyword in ' '.join(features).lower() for keyword in ['scientific', 'sin', 'cos', 'tan']):
                try:
                    await page.click('text=C')
                    await page.click('text=9')
                    await page.click('text=0')
                    await page.click('text=sin', timeout=2000)
                    display = await page.locator('input[type="text"], .display, #display').first.input_value()
                    if display and display != '90':
                        passed_tests.append("Scientific functions (sin) working")
                    else:
                        failed_tests.append("Scientific functions not working")
                except Exception:
                    failed_tests.append("Scientific functions missing or broken")
                    critical_issues.append("Scientific functions advertised but not working")
            
            # Test 4: Memory functions
            if any(keyword in ' '.join(features).lower() for keyword in ['memory', 'm+', 'mr']):
                try:
                    await page.click('text=C')
                    await page.click('text=5')
                    await page.click('text=M+', timeout=2000)
                    await page.click('text=C')
                    await page.click('text=MR')
                    display = await page.locator('input[type="text"], .display, #display').first.input_value()
                    if '5' in display:
                        passed_tests.append("Memory functions (M+/MR) working")
                    else:
                        failed_tests.append("Memory functions not working correctly")
                except Exception:
                    failed_tests.append("Memory functions missing")
                    if 'memory' in ' '.join(features).lower():
                        critical_issues.append("Memory functions advertised but not implemented")
            
            # Test 5: Keyboard support
            try:
                await page.keyboard.press('Escape')
                await page.keyboard.type('5+5')
                await page.keyboard.press('Enter')
                display = await page.locator('input[type="text"], .display, #display').first.input_value()
                if '10' in display:
                    passed_tests.append("Keyboard shortcuts working")
                else:
                    failed_tests.append("Keyboard shortcuts not working")
            except Exception:
                failed_tests.append("Keyboard shortcuts missing")
            
            # Test 6: Clear function
            try:
                await page.click('text=C')
                display = await page.locator('input[type="text"], .display, #display').first.input_value()
                if display in ['0', '', '0.']:
                    passed_tests.append("Clear button working")
                else:
                    failed_tests.append("Clear button not working properly")
            except Exception:
                failed_tests.append("Clear button missing or broken")
                critical_issues.append("Basic clear functionality broken")
            
        except Exception as e:
            critical_issues.append(f"Calculator testing error: {str(e)}")
        
        return {
            "success": len(critical_issues) == 0,
            "passed": len(passed_tests),
            "failed": len(failed_tests),
            "total": len(passed_tests) + len(failed_tests),
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "critical_issues": critical_issues,
            "coverage_percent": (len(passed_tests) / max(len(passed_tests) + len(failed_tests), 1)) * 100
        }
    
    async def _test_todo_app(self, page: Page, features: List[str]) -> Dict:
        """Test todo app features"""
        passed_tests = []
        failed_tests = []
        critical_issues = []
        
        try:
            # Test 1: Add task
            try:
                await page.fill('input[type="text"], input[placeholder*="task" i], input[placeholder*="todo" i]', 'Test Task')
                await page.click('button:has-text("Add"), button:has-text("+"), button[type="submit"]')
                task_exists = await page.locator('text=Test Task').count() > 0
                if task_exists:
                    passed_tests.append("Add task working")
                else:
                    failed_tests.append("Add task not working")
                    critical_issues.append("Cannot add tasks - core functionality broken")
            except Exception as e:
                failed_tests.append("Add task failed")
                critical_issues.append(f"Task creation broken: {str(e)}")
            
            # Test 2: Mark complete
            try:
                checkbox = await page.locator('input[type="checkbox"]').first.is_visible()
                if checkbox:
                    await page.locator('input[type="checkbox"]').first.check()
                    passed_tests.append("Mark complete working")
                else:
                    failed_tests.append("Checkbox for completion not found")
            except Exception:
                failed_tests.append("Mark complete not working")
            
            # Test 3: Persistence (localStorage)
            if any(keyword in ' '.join(features).lower() for keyword in ['persist', 'storage', 'save']):
                try:
                    storage = await page.evaluate('() => localStorage.length')
                    if storage > 0:
                        passed_tests.append("localStorage persistence working")
                    else:
                        failed_tests.append("localStorage not being used")
                except Exception:
                    failed_tests.append("Persistence not working")
            
        except Exception as e:
            critical_issues.append(f"Todo app testing error: {str(e)}")
        
        return {
            "success": len(critical_issues) == 0,
            "passed": len(passed_tests),
            "failed": len(failed_tests),
            "total": len(passed_tests) + len(failed_tests),
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "critical_issues": critical_issues,
            "coverage_percent": (len(passed_tests) / max(len(passed_tests) + len(failed_tests), 1)) * 100
        }
    
    async def _test_dashboard(self, page: Page, features: List[str]) -> Dict:
        """Test dashboard features"""
        passed_tests = []
        failed_tests = []
        critical_issues = []
        
        try:
            # Test 1: Data display
            cards = await page.locator('.card, .metric, .widget').count()
            if cards > 0:
                passed_tests.append(f"Data cards visible ({cards} found)")
            else:
                failed_tests.append("No data cards found")
                critical_issues.append("Dashboard has no visible content")
            
            # Test 2: Charts/visualizations
            if any(keyword in ' '.join(features).lower() for keyword in ['chart', 'graph', 'visualiz']):
                canvas = await page.locator('canvas').count()
                if canvas > 0:
                    passed_tests.append("Charts/visualizations present")
                else:
                    failed_tests.append("Charts advertised but not found")
            
        except Exception as e:
            critical_issues.append(f"Dashboard testing error: {str(e)}")
        
        return {
            "success": len(critical_issues) == 0,
            "passed": len(passed_tests),
            "failed": len(failed_tests),
            "total": len(passed_tests) + len(failed_tests),
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "critical_issues": critical_issues,
            "coverage_percent": (len(passed_tests) / max(len(passed_tests) + len(failed_tests), 1)) * 100
        }
    
    async def _test_game(self, page: Page, features: List[str]) -> Dict:
        """Test game features"""
        passed_tests = []
        failed_tests = []
        critical_issues = []
        
        try:
            # Test 1: Game canvas/area
            canvas = await page.locator('canvas, #game, .game-area').count()
            if canvas > 0:
                passed_tests.append("Game area visible")
            else:
                failed_tests.append("No game area found")
                critical_issues.append("Game has no visible play area")
            
            # Test 2: Controls/buttons
            buttons = await page.locator('button').count()
            if buttons > 0:
                passed_tests.append("Control buttons present")
            else:
                failed_tests.append("No control buttons")
            
            # Test 3: Score display
            if any(keyword in ' '.join(features).lower() for keyword in ['score', 'points']):
                score = await page.locator('text=/score|points/i').count()
                if score > 0:
                    passed_tests.append("Score system visible")
                else:
                    failed_tests.append("Score system not found")
            
        except Exception as e:
            critical_issues.append(f"Game testing error: {str(e)}")
        
        return {
            "success": len(critical_issues) == 0,
            "passed": len(passed_tests),
            "failed": len(failed_tests),
            "total": len(passed_tests) + len(failed_tests),
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "critical_issues": critical_issues,
            "coverage_percent": (len(passed_tests) / max(len(passed_tests) + len(failed_tests), 1)) * 100
        }
    
    async def _test_generic_app(self, page: Page, features: List[str]) -> Dict:
        """Test generic app features"""
        passed_tests = []
        failed_tests = []
        critical_issues = []
        
        try:
            # Test 1: Page loads
            title = await page.title()
            if title:
                passed_tests.append(f"Page loads (title: {title})")
            else:
                failed_tests.append("Page has no title")
            
            # Test 2: Interactive elements
            buttons = await page.locator('button, input, select').count()
            if buttons > 0:
                passed_tests.append(f"Interactive elements present ({buttons} found)")
            else:
                failed_tests.append("No interactive elements found")
                critical_issues.append("App has no buttons or inputs")
            
            # Test 3: Content visible
            text_content = await page.text_content('body')
            if text_content and len(text_content) > 50:
                passed_tests.append("Content visible on page")
            else:
                failed_tests.append("Page appears empty")
                critical_issues.append("App has no visible content")
            
        except Exception as e:
            critical_issues.append(f"Generic app testing error: {str(e)}")
        
        return {
            "success": len(critical_issues) == 0,
            "passed": len(passed_tests),
            "failed": len(failed_tests),
            "total": len(passed_tests) + len(failed_tests),
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "critical_issues": critical_issues,
            "coverage_percent": (len(passed_tests) / max(len(passed_tests) + len(failed_tests), 1)) * 100
        }
    
    async def _start_local_server(self, app_path: Path):
        """Start a local HTTP server to serve the app"""
        import os
        
        class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, directory=str(app_path), **kwargs)
            
            def log_message(self, format, *args):
                pass
        
        self.server = socketserver.TCPServer(("", self.test_port), CustomHTTPRequestHandler)
        self.server_thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.server_thread.start()
        
        await asyncio.sleep(0.5)
        logger.info(f"📡 Test server started on http://localhost:{self.test_port}")
    
    def _stop_local_server(self):
        """Stop the local HTTP server"""
        if self.server:
            self.server.shutdown()
            self.server.server_close()
            logger.info("🛑 Test server stopped")
