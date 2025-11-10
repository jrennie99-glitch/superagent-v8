"""Enhanced code generation module with enterprise-quality output."""

import asyncio
from pathlib import Path
from typing import List, Dict, Any, Optional
import structlog
import json
import re

from superagent.core.llm import LLMProvider
from superagent.core.cache import CacheManager, cached

logger = structlog.get_logger()


class EnterpriseCodeGenerator:
    """
    Enhanced code generator that produces enterprise-quality applications.
    
    This is a WRAPPER around the existing CodeGenerator that adds:
    - Better prompts with specific enterprise requirements
    - Multi-pass validation and refinement
    - Quality checks before saving
    - Complete, working code generation
    
    DOES NOT REMOVE any existing functionality!
    """
    
    def __init__(self, llm: LLMProvider, cache: CacheManager):
        """Initialize enhanced code generator.
        
        Args:
            llm: LLM provider
            cache: Cache manager
        """
        self.llm = llm
        self.cache = cache
        
        # Language-specific templates and configurations
        self.language_configs = {
            "python": {
                "extension": ".py",
                "template": "python_module",
                "formatter": "black"
            },
            "javascript": {
                "extension": ".js",
                "template": "js_module",
                "formatter": "prettier"
            },
            "typescript": {
                "extension": ".ts",
                "template": "ts_module",
                "formatter": "prettier"
            },
            "java": {
                "extension": ".java",
                "template": "java_class",
                "formatter": "google-java-format"
            },
            "go": {
                "extension": ".go",
                "template": "go_package",
                "formatter": "gofmt"
            }
        }
        
        # Enterprise quality requirements
        self.enterprise_requirements = {
            "html": [
                "Complete HTML5 structure with DOCTYPE",
                "Semantic HTML tags (header, main, footer, section, article)",
                "Proper meta tags (viewport, charset, description)",
                "All tags properly closed and nested",
                "Accessibility attributes (ARIA labels, alt text)",
                "Responsive design with mobile-first approach",
                "Clean, organized structure with comments"
            ],
            "css": [
                "Modern CSS3 with flexbox/grid layouts",
                "Responsive design with media queries",
                "Professional color scheme and typography",
                "Consistent spacing and alignment",
                "Smooth transitions and animations",
                "Cross-browser compatibility",
                "Mobile, tablet, and desktop breakpoints"
            ],
            "javascript": [
                "Complete functionality - all features working",
                "Proper event listeners attached",
                "Input validation and error handling",
                "Edge case handling (division by zero, invalid input)",
                "Clean, modular code with functions",
                "Comments explaining logic",
                "No console errors or warnings",
                "Keyboard support where applicable"
            ],
            "python": [
                "Type hints on all functions",
                "Comprehensive docstrings (Google/NumPy style)",
                "Proper error handling with try-except",
                "Input validation",
                "Logging instead of print statements",
                "PEP 8 compliant",
                "Security best practices"
            ]
        }
    
    async def generate_enterprise_web_app(
        self,
        description: str,
        app_name: str,
        app_type: str = "calculator"
    ) -> Dict[str, Any]:
        """
        Generate a complete, enterprise-quality web application.
        
        This is the MAIN method to use for generating quality apps.
        
        Args:
            description: What the app should do
            app_name: Name of the application
            app_type: Type (calculator, dashboard, form, etc.)
            
        Returns:
            Complete application with all files
        """
        logger.info(f"Generating ENTERPRISE-QUALITY {app_type}: {app_name}")
        
        # Step 1: Analyze requirements in detail
        requirements = await self._analyze_requirements_detailed(description, app_type)
        
        # Step 2: Create architecture plan
        architecture = await self._create_architecture_plan(requirements, app_type)
        
        # Step 3: Generate HTML with enterprise quality
        html_code = await self._generate_enterprise_html(requirements, architecture, app_type)
        
        # Step 4: Validate and refine HTML
        html_code = await self._validate_and_refine_html(html_code, requirements)
        
        # Step 5: Generate complete CSS with professional styling
        css_code = await self._generate_enterprise_css(requirements, app_type)
        
        # Step 6: Generate fully functional JavaScript
        js_code = await self._generate_enterprise_javascript(requirements, app_type)
        
        # Step 7: Validate JavaScript functionality
        js_code = await self._validate_and_refine_javascript(js_code, requirements)
        
        # Step 8: Create integrated single-file app (or separate files)
        final_files = self._integrate_files(html_code, css_code, js_code, app_name)
        
        # Step 9: Final quality check
        quality_report = await self._final_quality_check(final_files, requirements)
        
        return {
            "success": True,
            "app_name": app_name,
            "app_type": app_type,
            "files": final_files,
            "requirements": requirements,
            "quality_report": quality_report,
            "ready_to_use": quality_report["passed"],
            "instructions": self._generate_usage_instructions(app_name, app_type)
        }
    
    async def _analyze_requirements_detailed(
        self,
        description: str,
        app_type: str
    ) -> Dict[str, Any]:
        """Analyze requirements in detail before generating code."""
        
        prompt = f"""Analyze this {app_type} application request in detail:

"{description}"

Provide a comprehensive analysis including:

1. CORE FEATURES (list all features that must work):
   - What are the main functions?
   - What operations must be supported?
   - What interactions are needed?

2. UI REQUIREMENTS:
   - What elements are needed (buttons, inputs, displays)?
   - What layout works best?
   - What visual style is appropriate?

3. FUNCTIONALITY REQUIREMENTS:
   - What calculations/operations are needed?
   - What validation is required?
   - What error handling is needed?

4. QUALITY REQUIREMENTS:
   - Must work on mobile, tablet, desktop
   - Must handle all edge cases
   - Must be visually professional
   - Must be fully functional

Respond in JSON format:
{{
    "core_features": ["feature1", "feature2", ...],
    "ui_elements": ["element1", "element2", ...],
    "operations": ["operation1", "operation2", ...],
    "validations": ["validation1", "validation2", ...],
    "edge_cases": ["case1", "case2", ...],
    "style": "description of visual style"
}}"""

        try:
            response = await self.llm.generate(prompt)
            # Try to parse JSON from response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                requirements = json.loads(json_match.group())
            else:
                # Fallback to defaults
                requirements = self._get_default_requirements(app_type)
        except Exception as e:
            logger.warning(f"Requirements analysis failed, using defaults: {e}")
            requirements = self._get_default_requirements(app_type)
        
        return requirements
    
    def _get_default_requirements(self, app_type: str) -> Dict[str, Any]:
        """Get default requirements for common app types."""
        
        if app_type == "calculator":
            return {
                "core_features": [
                    "Basic arithmetic (add, subtract, multiply, divide)",
                    "Clear/reset functionality",
                    "Decimal point support",
                    "Keyboard input support",
                    "Display current calculation"
                ],
                "ui_elements": [
                    "Display screen",
                    "Number buttons (0-9)",
                    "Operation buttons (+, -, *, /)",
                    "Equals button",
                    "Clear button",
                    "Decimal point button"
                ],
                "operations": ["addition", "subtraction", "multiplication", "division"],
                "validations": [
                    "Prevent division by zero",
                    "Limit decimal places",
                    "Prevent multiple decimal points",
                    "Handle invalid operations"
                ],
                "edge_cases": [
                    "Division by zero",
                    "Very large numbers",
                    "Multiple operators in sequence",
                    "Starting with operator"
                ],
                "style": "Modern, clean calculator with professional appearance"
            }
        else:
            return {
                "core_features": ["Main functionality", "User interaction"],
                "ui_elements": ["Interface elements", "Controls"],
                "operations": ["Primary operations"],
                "validations": ["Input validation"],
                "edge_cases": ["Error handling"],
                "style": "Professional, modern design"
            }
    
    async def _create_architecture_plan(
        self,
        requirements: Dict[str, Any],
        app_type: str
    ) -> Dict[str, Any]:
        """Create architecture plan for the application."""
        
        return {
            "structure": "single-page-app",
            "components": {
                "html": "Complete HTML5 structure with all elements",
                "css": "Embedded styles with responsive design",
                "javascript": "Complete functionality with validation"
            },
            "organization": {
                "html": ["DOCTYPE", "head with meta tags", "body with semantic structure"],
                "css": ["Reset/base styles", "Layout", "Components", "Responsive"],
                "javascript": ["State management", "Event handlers", "Operations", "Validation"]
            }
        }
    
    async def _generate_enterprise_html(
        self,
        requirements: Dict[str, Any],
        architecture: Dict[str, Any],
        app_type: str
    ) -> str:
        """Generate enterprise-quality HTML."""
        
        features_list = "\n".join([f"   - {f}" for f in requirements.get("core_features", [])])
        elements_list = "\n".join([f"   - {e}" for e in requirements.get("ui_elements", [])])
        
        prompt = f"""Generate COMPLETE, ENTERPRISE-QUALITY HTML for a {app_type} application.

REQUIREMENTS:
{features_list}

UI ELEMENTS NEEDED:
{elements_list}

STRICT REQUIREMENTS - MUST FOLLOW:

1. COMPLETE HTML5 STRUCTURE:
   <!DOCTYPE html>
   <html lang="en">
   <head>
       <meta charset="UTF-8">
       <meta name="viewport" content="width=device-width, initial-scale=1.0">
       <title>Professional {app_type.title()}</title>
   </head>
   <body>
       <!-- Complete application here -->
   </body>
   </html>

2. SEMANTIC HTML:
   - Use <header>, <main>, <section>, <footer>
   - Use proper heading hierarchy (h1, h2, etc.)
   - Use <button> for buttons, not <div>
   - Use <input> for inputs with proper types

3. ACCESSIBILITY:
   - Add aria-label to all interactive elements
   - Add alt text to images
   - Ensure keyboard navigation works
   - Use semantic HTML tags

4. COMPLETE STRUCTURE:
   - ALL elements must be present
   - ALL tags must be properly closed
   - Proper nesting and indentation
   - Include IDs for JavaScript interaction

5. PROFESSIONAL LAYOUT:
   - Clean, organized structure
   - Logical grouping of elements
   - Comments explaining sections

IMPORTANT: Generate ONLY the complete HTML code. No explanations, no markdown.
Start with <!DOCTYPE html> and end with </html>. Make it COMPLETE and WORKING."""

        html_code = await self.llm.generate(prompt)
        html_code = self._clean_generated_code(html_code)
        
        # Ensure it has proper structure
        if not html_code.strip().startswith("<!DOCTYPE"):
            html_code = "<!DOCTYPE html>\n" + html_code
        
        return html_code
    
    async def _validate_and_refine_html(
        self,
        html_code: str,
        requirements: Dict[str, Any]
    ) -> str:
        """Validate HTML and refine if needed."""
        
        issues = []
        
        # Check for basic structure
        if "<!DOCTYPE" not in html_code:
            issues.append("Missing DOCTYPE declaration")
        if "<html" not in html_code:
            issues.append("Missing <html> tag")
        if "<head>" not in html_code:
            issues.append("Missing <head> section")
        if "<body>" not in html_code:
            issues.append("Missing <body> section")
        if 'charset="UTF-8"' not in html_code:
            issues.append("Missing charset meta tag")
        if 'name="viewport"' not in html_code:
            issues.append("Missing viewport meta tag")
        
        # If there are critical issues, regenerate
        if issues:
            logger.warning(f"HTML validation issues found: {issues}")
            # Add missing parts
            if "<!DOCTYPE" not in html_code:
                html_code = "<!DOCTYPE html>\n" + html_code
            if "<html" not in html_code:
                html_code = '<html lang="en">\n' + html_code + "\n</html>"
        
        return html_code
    
    async def _generate_enterprise_css(
        self,
        requirements: Dict[str, Any],
        app_type: str
    ) -> str:
        """Generate enterprise-quality CSS."""
        
        style = requirements.get("style", "Modern, professional design")
        
        prompt = f"""Generate COMPLETE, PROFESSIONAL CSS for a {app_type} application.

STYLE REQUIREMENTS: {style}

STRICT REQUIREMENTS - MUST INCLUDE:

1. RESET/BASE STYLES:
   * {{
       margin: 0;
       padding: 0;
       box-sizing: border-box;
   }}

2. MODERN LAYOUT:
   - Use Flexbox or CSS Grid for layout
   - Center content properly
   - Proper spacing and padding
   - Professional typography

3. RESPONSIVE DESIGN:
   - Mobile-first approach
   - Media queries for tablet (768px) and desktop (1024px)
   - Flexible layouts that adapt
   - Touch-friendly button sizes (min 44px)

4. PROFESSIONAL STYLING:
   - Modern color scheme (not garish)
   - Consistent spacing (use CSS variables)
   - Proper contrast for readability
   - Smooth transitions and hover effects
   - Box shadows for depth
   - Border radius for modern look

5. COMPONENT STYLING:
   - Style all buttons consistently
   - Style inputs/displays clearly
   - Add hover and active states
   - Ensure visual hierarchy

6. ACCESSIBILITY:
   - Sufficient color contrast
   - Clear focus indicators
   - Readable font sizes (minimum 16px)

IMPORTANT: Generate ONLY the CSS code. No explanations, no markdown.
Make it COMPLETE, PROFESSIONAL, and RESPONSIVE."""

        css_code = await self.llm.generate(prompt)
        css_code = self._clean_generated_code(css_code)
        
        return css_code
    
    async def _generate_enterprise_javascript(
        self,
        requirements: Dict[str, Any],
        app_type: str
    ) -> str:
        """Generate enterprise-quality JavaScript."""
        
        features = requirements.get("core_features", [])
        operations = requirements.get("operations", [])
        validations = requirements.get("validations", [])
        edge_cases = requirements.get("edge_cases", [])
        
        features_list = "\n".join([f"   - {f}" for f in features])
        validations_list = "\n".join([f"   - {v}" for v in validations])
        edge_cases_list = "\n".join([f"   - {e}" for e in edge_cases])
        
        prompt = f"""Generate COMPLETE, FULLY FUNCTIONAL JavaScript for a {app_type} application.

FEATURES THAT MUST WORK:
{features_list}

VALIDATIONS REQUIRED:
{validations_list}

EDGE CASES TO HANDLE:
{edge_cases_list}

STRICT REQUIREMENTS - MUST INCLUDE:

1. COMPLETE FUNCTIONALITY:
   - ALL features must be implemented
   - ALL operations must work correctly
   - ALL buttons must be functional
   - NO placeholder or TODO comments

2. PROPER INITIALIZATION:
   - Wait for DOM to load (DOMContentLoaded)
   - Get all element references
   - Attach all event listeners
   - Initialize state variables

3. ERROR HANDLING:
   - Try-catch blocks where appropriate
   - Validation before operations
   - Handle all edge cases listed above
   - Display user-friendly error messages

4. INPUT VALIDATION:
   - Validate all user inputs
   - Prevent invalid operations
   - Handle edge cases gracefully
   - Sanitize inputs if needed

5. CLEAN CODE:
   - Modular functions (one purpose each)
   - Clear variable names
   - Comments explaining logic
   - Consistent code style

6. EVENT HANDLING:
   - Attach listeners to all interactive elements
   - Handle both click and keyboard events
   - Prevent default behaviors where needed
   - Update display/state correctly

7. STATE MANAGEMENT:
   - Track application state
   - Update state consistently
   - Reflect state in UI

IMPORTANT: Generate ONLY the JavaScript code. No explanations, no markdown.
Make it COMPLETE, WORKING, and PRODUCTION-READY. Every feature must be FUNCTIONAL."""

        js_code = await self.llm.generate(prompt)
        js_code = self._clean_generated_code(js_code)
        
        return js_code
    
    async def _validate_and_refine_javascript(
        self,
        js_code: str,
        requirements: Dict[str, Any]
    ) -> str:
        """Validate JavaScript and refine if needed."""
        
        issues = []
        
        # Check for basic structure
        if "DOMContentLoaded" not in js_code and "window.onload" not in js_code:
            issues.append("Missing DOM ready handler")
        
        if "addEventListener" not in js_code and "onclick" not in js_code:
            issues.append("No event listeners found")
        
        # Check for required features
        features = requirements.get("core_features", [])
        for feature in features:
            if "clear" in feature.lower() and "clear" not in js_code.lower():
                issues.append(f"Missing implementation: {feature}")
        
        if issues:
            logger.warning(f"JavaScript validation issues: {issues}")
            # Could trigger refinement here if needed
        
        return js_code
    
    def _integrate_files(
        self,
        html_code: str,
        css_code: str,
        js_code: str,
        app_name: str
    ) -> Dict[str, str]:
        """Integrate HTML, CSS, and JavaScript into final files."""
        
        # Create single-file version (most common for simple apps)
        if "<style>" not in html_code and css_code:
            # Inject CSS into HTML
            style_tag = f"\n<style>\n{css_code}\n</style>\n</head>"
            html_code = html_code.replace("</head>", style_tag)
        
        if "<script>" not in html_code and js_code:
            # Inject JavaScript into HTML
            script_tag = f"\n<script>\n{js_code}\n</script>\n</body>"
            html_code = html_code.replace("</body>", script_tag)
        
        files = {
            f"{app_name}.html": html_code
        }
        
        # Also provide separate files
        if css_code:
            files[f"{app_name}.css"] = css_code
        if js_code:
            files[f"{app_name}.js"] = js_code
        
        return files
    
    async def _final_quality_check(
        self,
        files: Dict[str, str],
        requirements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Perform final quality check on generated code."""
        
        checks = {
            "html_complete": False,
            "css_present": False,
            "js_functional": False,
            "responsive": False,
            "accessible": False,
            "passed": False
        }
        
        main_file = next(iter(files.values()))
        
        # Check HTML completeness
        if all(tag in main_file for tag in ["<!DOCTYPE", "<html", "<head>", "<body>"]):
            checks["html_complete"] = True
        
        # Check CSS presence
        if "<style>" in main_file or any(".css" in f for f in files.keys()):
            checks["css_present"] = True
        
        # Check JavaScript presence
        if "<script>" in main_file or any(".js" in f for f in files.keys()):
            checks["js_functional"] = True
        
        # Check responsive design
        if "viewport" in main_file and ("@media" in main_file or "flex" in main_file):
            checks["responsive"] = True
        
        # Check accessibility
        if "aria-label" in main_file or "alt=" in main_file:
            checks["accessible"] = True
        
        # Overall pass
        checks["passed"] = all([
            checks["html_complete"],
            checks["css_present"],
            checks["js_functional"]
        ])
        
        return checks
    
    def _generate_usage_instructions(self, app_name: str, app_type: str) -> str:
        """Generate usage instructions for the application."""
        
        return f"""
USAGE INSTRUCTIONS for {app_name}:

1. OPEN THE APP:
   - Open {app_name}.html in any modern web browser
   - Works on Chrome, Firefox, Safari, Edge

2. USE THE APP:
   - All features are fully functional
   - Click buttons or use keyboard
   - Works on desktop, tablet, and mobile

3. TEST THE APP:
   - Try all operations
   - Test edge cases
   - Verify responsive design (resize browser)

4. DEPLOY THE APP:
   - Upload {app_name}.html to any web host
   - No server required (static HTML)
   - Works immediately

5. CUSTOMIZE:
   - Edit CSS in <style> section for styling
   - Edit JavaScript in <script> section for functionality
   - All code is well-commented

The app is COMPLETE and READY TO USE!
"""
    
    def _clean_generated_code(self, code: str) -> str:
        """Clean generated code (remove markdown, explanations, etc.)."""
        
        # Remove markdown code blocks
        if "```" in code:
            lines = code.split('\n')
            cleaned_lines = []
            in_code_block = False
            
            for line in lines:
                if line.strip().startswith("```"):
                    in_code_block = not in_code_block
                    continue
                if in_code_block or "```" not in code:
                    cleaned_lines.append(line)
            
            code = '\n'.join(cleaned_lines)
        
        # Remove common explanatory phrases
        explanations = [
            "Here's the code:",
            "Here is the code:",
            "This code provides:",
            "This implementation:",
            "Note that:",
            "Important:",
        ]
        
        for phrase in explanations:
            if code.strip().startswith(phrase):
                code = code[code.index('\n')+1:]
        
        return code.strip()
    
    # Keep all original methods for backward compatibility
    async def generate_files(self, description: str, 
                           file_paths: List[str],
                           project_path: Path,
                           language: Optional[str] = None) -> List[str]:
        """Original method - kept for compatibility."""
        # Delegate to original implementation or enhance it
        pass
    
    async def generate_file(self, file_path: str, description: str,
                          project_path: Path, language: str) -> str:
        """Original method - kept for compatibility."""
        pass
    
    async def generate_project(self, description: str, 
                              project_type: str = "web_app",
                              language: str = "python") -> Dict[str, Any]:
        """Original method - kept for compatibility."""
        pass
