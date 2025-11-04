"""Advanced code generation module using Claude 3.5 Sonnet."""

import asyncio
from pathlib import Path
from typing import List, Dict, Any, Optional
import structlog

from superagent.core.llm import LLMProvider
from superagent.core.cache import CacheManager, cached

logger = structlog.get_logger()


class CodeGenerator:
    """High-performance code generation with multi-language support."""
    
    def __init__(self, llm: LLMProvider, cache: CacheManager):
        """Initialize code generator.
        
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
    
    async def generate_files(self, description: str, 
                           file_paths: List[str],
                           project_path: Path,
                           language: Optional[str] = None) -> List[str]:
        """Generate multiple files in parallel.
        
        Args:
            description: What to generate
            file_paths: List of file paths to generate
            project_path: Base project path
            language: Programming language (auto-detected if not provided)
            
        Returns:
            List of generated file paths
        """
        language = language or self._detect_language(file_paths)
        
        logger.info(
            "Generating files",
            count=len(file_paths),
            language=language,
            description=description[:100]
        )
        
        # Generate all files in parallel
        tasks = [
            self.generate_file(file_path, description, project_path, language)
            for file_path in file_paths
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        generated_files = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Failed to generate {file_paths[i]}: {result}")
            else:
                generated_files.append(result)
        
        return generated_files
    
    @cached(ttl=3600)
    async def generate_file(self, file_path: str, description: str,
                          project_path: Path, language: str) -> str:
        """Generate a single file.
        
        Args:
            file_path: Relative file path
            description: What to generate
            project_path: Base project path
            language: Programming language
            
        Returns:
            Path to generated file
        """
        full_path = project_path / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create context-aware prompt
        prompt = self._create_generation_prompt(
            file_path, description, language
        )
        
        system_prompt = f"""You are an expert {language} developer. Generate clean, 
efficient, production-ready code that follows best practices and style guidelines.

Requirements:
- Write clean, readable code with proper documentation
- Include error handling and edge cases
- Follow language-specific best practices
- Add type hints/annotations where applicable
- Include necessary imports
- Add comprehensive docstrings/comments

Provide ONLY the code, no explanations or markdown formatting."""
        
        # Generate code
        code = await self.llm.generate(prompt, system=system_prompt)
        
        # Clean up code (remove markdown if present)
        code = self._clean_generated_code(code)
        
        # Format code
        code = await self._format_code(code, language)
        
        # Write to file
        full_path.write_text(code)
        
        logger.info(f"Generated file: {file_path}")
        
        return str(full_path)
    
    async def generate_project(self, description: str, 
                              project_type: str = "web_app",
                              language: str = "python") -> Dict[str, Any]:
        """Generate entire project structure.
        
        Args:
            description: Project description
            project_type: Type of project (web_app, cli_tool, library, api)
            language: Primary programming language
            
        Returns:
            Project structure and files
        """
        logger.info(
            "Generating project",
            type=project_type,
            language=language
        )
        
        # Create project structure plan
        structure_prompt = f"""Create a complete project structure for a {project_type} 
in {language} based on this description: {description}

Include:
- All necessary files and directories
- Configuration files (requirements.txt, package.json, etc.)
- Source code structure
- Test directories
- Documentation files

Provide the structure as JSON:
{{
    "directories": ["dir1", "dir2", ...],
    "files": {{
        "path/to/file": "purpose of file",
        ...
    }},
    "dependencies": ["dep1", "dep2", ...]
}}"""
        
        structure = await self.llm.generate_structured(
            structure_prompt,
            schema={
                "directories": ["string"],
                "files": {"string": "string"},
                "dependencies": ["string"]
            }
        )
        
        return structure
    
    def _create_generation_prompt(self, file_path: str, 
                                 description: str, language: str) -> str:
        """Create generation prompt for a file.
        
        Args:
            file_path: File path
            description: Description
            language: Language
            
        Returns:
            Prompt
        """
        file_name = Path(file_path).name
        
        prompt = f"""Generate {language} code for file: {file_name}

Project Description: {description}

File Path: {file_path}

Generate complete, production-ready code for this file. Include:
- All necessary imports
- Proper error handling
- Documentation/docstrings
- Type hints/annotations
- Best practices for {language}

Code:"""
        
        return prompt
    
    def _clean_generated_code(self, code: str) -> str:
        """Clean generated code (remove markdown, etc.).
        
        Args:
            code: Raw generated code
            
        Returns:
            Cleaned code
        """
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
        
        return code.strip()
    
    async def _format_code(self, code: str, language: str) -> str:
        """Format code using language-specific formatter.
        
        Args:
            code: Code to format
            language: Programming language
            
        Returns:
            Formatted code
        """
        # Simple formatting - could integrate with actual formatters
        if language == "python":
            try:
                import black
                mode = black.Mode(line_length=88)
                code = black.format_str(code, mode=mode)
            except Exception as e:
                logger.warning(f"Black formatting failed: {e}")
        
        return code
    
    def _detect_language(self, file_paths: List[str]) -> str:
        """Detect language from file extensions.
        
        Args:
            file_paths: List of file paths
            
        Returns:
            Detected language
        """
        if not file_paths:
            return "python"
        
        extensions = {Path(fp).suffix for fp in file_paths}
        
        extension_map = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".java": "java",
            ".go": "go",
            ".rs": "rust",
            ".cpp": "cpp",
            ".c": "c"
        }
        
        for ext in extensions:
            if ext in extension_map:
                return extension_map[ext]
        
        return "python"





