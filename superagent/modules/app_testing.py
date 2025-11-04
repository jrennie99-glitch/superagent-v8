"""
App Testing Module - Automated Browser Testing
Tests apps using real browser with Playwright
Provides video replay and visual feedback
"""

import logging
import asyncio
from typing import Dict, List, Optional
from pathlib import Path
import json
from datetime import datetime

logger = logging.getLogger(__name__)


class AppTesting:
    """
    Automated testing with real browser
    Features:
    - Playwright browser automation
    - Video recording of tests
    - Screenshot capture
    - Auto-fix issues
    - Interactive replay
    """
    
    def __init__(self):
        self.test_results = []
        self.playwright_available = False
        self.recording_enabled = True
        
        # Check if Playwright is available
        try:
            import playwright
            self.playwright_available = True
        except ImportError:
            logger.warning("Playwright not installed. Browser testing unavailable.")
    
    async def run_browser_test(self, 
                               url: str, 
                               test_scenarios: List[Dict],
                               record_video: bool = True) -> Dict:
        """
        Run automated browser tests
        
        Args:
            url: URL to test
            test_scenarios: List of test scenarios to execute
            record_video: Whether to record video of tests
        
        Returns:
            Test results with video and screenshots
        """
        if not self.playwright_available:
            return {
                "success": False,
                "error": "Playwright not installed. Install with: pip install playwright && playwright install"
            }
        
        try:
            from playwright.async_api import async_playwright
            
            results = {
                "success": True,
                "url": url,
                "tests_run": 0,
                "tests_passed": 0,
                "tests_failed": 0,
                "issues_found": [],
                "auto_fixes": [],
                "screenshots": [],
                "video_path": None,
                "timestamp": datetime.now().isoformat()
            }
            
            async with async_playwright() as p:
                # Launch browser
                browser = await p.chromium.launch(headless=True)
                
                # Set up recording if enabled
                context_options = {}
                if record_video:
                    context_options['record_video_dir'] = 'test_recordings'
                    context_options['record_video_size'] = {"width": 1280, "height": 720}
                
                context = await browser.new_context(**context_options)
                page = await context.new_page()
                
                # Navigate to URL
                try:
                    await page.goto(url, wait_until='networkidle', timeout=10000)
                    results['tests_run'] += 1
                    results['tests_passed'] += 1
                except Exception as e:
                    results['issues_found'].append({
                        "type": "navigation_error",
                        "message": f"Failed to load page: {str(e)}"
                    })
                    results['tests_failed'] += 1
                
                # Run test scenarios
                for i, scenario in enumerate(test_scenarios):
                    try:
                        await self._execute_test_scenario(page, scenario, results)
                        results['tests_run'] += 1
                        results['tests_passed'] += 1
                    except Exception as e:
                        results['tests_failed'] += 1
                        results['issues_found'].append({
                            "scenario": scenario.get('name', f'Test {i+1}'),
                            "error": str(e)
                        })
                
                # Take final screenshot
                screenshot_path = f"test_screenshots/final_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                await page.screenshot(path=screenshot_path)
                results['screenshots'].append(screenshot_path)
                
                # Get video path if recording
                if record_video:
                    video_path = await page.video.path()
                    results['video_path'] = str(video_path)
                
                await context.close()
                await browser.close()
            
            # Auto-fix issues if any found
            if results['issues_found']:
                await self._auto_fix_issues(results)
            
            self.test_results.append(results)
            return results
            
        except Exception as e:
            logger.error(f"Browser testing failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "install_command": "pip install playwright && playwright install chromium"
            }
    
    async def _execute_test_scenario(self, page, scenario: Dict, results: Dict):
        """Execute a single test scenario"""
        action = scenario.get('action')
        
        if action == 'click':
            selector = scenario.get('selector')
            await page.click(selector)
        elif action == 'fill':
            selector = scenario.get('selector')
            value = scenario.get('value')
            await page.fill(selector, value)
        elif action == 'check_text':
            text = scenario.get('text')
            locator = page.locator(f"text={text}")
            await locator.wait_for(timeout=5000)
        elif action == 'screenshot':
            name = scenario.get('name', 'test')
            screenshot_path = f"test_screenshots/{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            await page.screenshot(path=screenshot_path)
            results['screenshots'].append(screenshot_path)
    
    async def _auto_fix_issues(self, results: Dict):
        """Attempt to automatically fix found issues"""
        for issue in results['issues_found']:
            fix = await self._suggest_fix(issue)
            if fix:
                results['auto_fixes'].append(fix)
    
    async def _suggest_fix(self, issue: Dict) -> Optional[Dict]:
        """Suggest fix for an issue"""
        issue_type = issue.get('type')
        
        if issue_type == 'navigation_error':
            return {
                "issue": issue,
                "suggested_fix": "Check if server is running and URL is correct",
                "code_change": "Ensure the app is served on correct port (5000)"
            }
        
        return None
    
    def generate_test_scenarios(self, app_type: str, description: str) -> List[Dict]:
        """
        Auto-generate test scenarios based on app description
        
        Args:
            app_type: Type of application
            description: App description
        
        Returns:
            List of test scenarios
        """
        scenarios = []
        
        if app_type == 'webapp':
            scenarios = [
                {"name": "Load homepage", "action": "check_text", "text": ""},
                {"name": "Check responsiveness", "action": "screenshot", "name": "desktop"},
            ]
        elif app_type == 'api':
            scenarios = [
                {"name": "Check API health", "action": "check_text", "text": "healthy"},
            ]
        
        return scenarios
    
    def get_test_report(self) -> Dict:
        """Get comprehensive test report"""
        return {
            "total_tests": len(self.test_results),
            "recent_tests": self.test_results[-5:],
            "summary": {
                "total_passed": sum(r['tests_passed'] for r in self.test_results),
                "total_failed": sum(r['tests_failed'] for r in self.test_results),
                "issues_found": sum(len(r['issues_found']) for r in self.test_results)
            }
        }


# Global instance
app_testing_instance = AppTesting()


def test_app(url: str, app_type: str = 'webapp', custom_scenarios: List[Dict] = None) -> Dict:
    """
    Test an application with automated browser testing
    
    Args:
        url: URL to test
        app_type: Type of application
        custom_scenarios: Custom test scenarios (optional)
    
    Returns:
        Test results
    """
    scenarios = custom_scenarios or app_testing_instance.generate_test_scenarios(app_type, "")
    
    # Run async test
    loop = asyncio.get_event_loop()
    if loop.is_running():
        # If loop is already running, create a task
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(
                asyncio.run,
                app_testing_instance.run_browser_test(url, scenarios)
            )
            return future.result()
    else:
        return loop.run_until_complete(
            app_testing_instance.run_browser_test(url, scenarios)
        )
