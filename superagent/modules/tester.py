"""Automated testing engine with test generation."""

import asyncio
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional
import structlog

from superagent.core.config import TestingConfig

logger = structlog.get_logger()


class TestingEngine:
    """Automated testing with test case generation."""
    
    def __init__(self, config: TestingConfig):
        """Initialize testing engine.
        
        Args:
            config: Testing configuration
        """
        self.config = config
        
    async def run_tests(self, project_path: Path) -> Dict[str, Any]:
        """Run tests for a project.
        
        Args:
            project_path: Path to project
            
        Returns:
            Test results
        """
        logger.info("Running tests", path=str(project_path))
        
        # Detect test framework
        framework = self._detect_framework(project_path)
        
        if framework == "pytest":
            return await self._run_pytest(project_path)
        elif framework == "jest":
            return await self._run_jest(project_path)
        elif framework == "junit":
            return await self._run_junit(project_path)
        else:
            logger.warning(f"Unsupported test framework: {framework}")
            return {"success": False, "error": "Unsupported framework"}
    
    async def _run_pytest(self, project_path: Path) -> Dict[str, Any]:
        """Run pytest tests.
        
        Args:
            project_path: Project path
            
        Returns:
            Test results
        """
        try:
            # Run pytest with coverage
            result = subprocess.run(
                ["pytest", "-v", "--cov=.", "--cov-report=json"],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            # Parse results
            passed = result.returncode == 0
            
            # Try to read coverage report
            coverage_file = project_path / "coverage.json"
            coverage_data = {}
            if coverage_file.exists():
                import json
                coverage_data = json.loads(coverage_file.read_text())
            
            return {
                "success": passed,
                "framework": "pytest",
                "stdout": result.stdout,
                "stderr": result.stderr,
                "coverage": coverage_data.get("totals", {}).get("percent_covered", 0),
                "exit_code": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Tests timed out"}
        except Exception as e:
            logger.error(f"Pytest execution failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _run_jest(self, project_path: Path) -> Dict[str, Any]:
        """Run Jest tests.
        
        Args:
            project_path: Project path
            
        Returns:
            Test results
        """
        try:
            result = subprocess.run(
                ["npm", "test", "--", "--coverage", "--json"],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            return {
                "success": result.returncode == 0,
                "framework": "jest",
                "stdout": result.stdout,
                "stderr": result.stderr,
                "exit_code": result.returncode
            }
        except Exception as e:
            logger.error(f"Jest execution failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _run_junit(self, project_path: Path) -> Dict[str, Any]:
        """Run JUnit tests.
        
        Args:
            project_path: Project path
            
        Returns:
            Test results
        """
        try:
            result = subprocess.run(
                ["mvn", "test"],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            return {
                "success": result.returncode == 0,
                "framework": "junit",
                "stdout": result.stdout,
                "stderr": result.stderr,
                "exit_code": result.returncode
            }
        except Exception as e:
            logger.error(f"JUnit execution failed: {e}")
            return {"success": False, "error": str(e)}
    
    def _detect_framework(self, project_path: Path) -> str:
        """Detect test framework from project structure.
        
        Args:
            project_path: Project path
            
        Returns:
            Framework name
        """
        # Check for pytest
        if (project_path / "pytest.ini").exists() or \
           (project_path / "setup.cfg").exists() or \
           list(project_path.rglob("test_*.py")):
            return "pytest"
        
        # Check for Jest
        if (project_path / "package.json").exists():
            return "jest"
        
        # Check for JUnit
        if (project_path / "pom.xml").exists():
            return "junit"
        
        # Default to pytest for Python projects
        if list(project_path.rglob("*.py")):
            return "pytest"
        
        return "unknown"
    
    async def generate_tests(self, source_file: Path, 
                           llm_provider) -> str:
        """Generate test cases for a source file using AI.
        
        Args:
            source_file: Source file to test
            llm_provider: LLM provider for generation
            
        Returns:
            Path to generated test file
        """
        logger.info(f"Generating tests for {source_file}")
        
        code = source_file.read_text()
        
        prompt = f"""Generate comprehensive unit tests for this code:

{code}

Requirements:
- Use pytest framework
- Include edge cases
- Test error handling
- Aim for {self.config.coverage_threshold}% coverage
- Include fixtures if needed
- Add docstrings

Provide ONLY the test code:"""
        
        test_code = await llm_provider.generate(prompt)
        
        # Save test file
        test_file = source_file.parent / f"test_{source_file.name}"
        test_file.write_text(test_code)
        
        logger.info(f"Generated test file: {test_file}")
        
        return str(test_file)





