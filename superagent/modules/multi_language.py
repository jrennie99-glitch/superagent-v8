"""
Multi-Language Code Generation Module

Supports Python, JavaScript/TypeScript, Go, Rust, and more.
This expands SuperAgent beyond Python-only to compete with top agents!
"""

from typing import Dict, Any, List, Optional
from pathlib import Path
import structlog

logger = structlog.get_logger()


class LanguageConfig:
    """Configuration for each supported language."""
    
    LANGUAGES = {
        "python": {
            "extensions": [".py"],
            "test_framework": "pytest",
            "package_file": "requirements.txt",
            "entry_point": "main.py",
            "docker_image": "python:3.11-slim",
            "install_cmd": "pip install -r requirements.txt",
            "run_cmd": "python main.py",
            "test_cmd": "pytest",
            "comment_style": "#"
        },
        "javascript": {
            "extensions": [".js", ".mjs"],
            "test_framework": "jest",
            "package_file": "package.json",
            "entry_point": "index.js",
            "docker_image": "node:18-slim",
            "install_cmd": "npm install",
            "run_cmd": "node index.js",
            "test_cmd": "npm test",
            "comment_style": "//"
        },
        "typescript": {
            "extensions": [".ts"],
            "test_framework": "jest",
            "package_file": "package.json",
            "entry_point": "index.ts",
            "docker_image": "node:18-slim",
            "install_cmd": "npm install",
            "run_cmd": "npx ts-node index.ts",
            "test_cmd": "npm test",
            "comment_style": "//"
        },
        "go": {
            "extensions": [".go"],
            "test_framework": "go test",
            "package_file": "go.mod",
            "entry_point": "main.go",
            "docker_image": "golang:1.21-alpine",
            "install_cmd": "go mod download",
            "run_cmd": "go run main.go",
            "test_cmd": "go test ./...",
            "comment_style": "//"
        },
        "rust": {
            "extensions": [".rs"],
            "test_framework": "cargo test",
            "package_file": "Cargo.toml",
            "entry_point": "main.rs",
            "docker_image": "rust:1.75-slim",
            "install_cmd": "cargo build",
            "run_cmd": "cargo run",
            "test_cmd": "cargo test",
            "comment_style": "//"
        },
        "java": {
            "extensions": [".java"],
            "test_framework": "junit",
            "package_file": "pom.xml",
            "entry_point": "Main.java",
            "docker_image": "openjdk:17-slim",
            "install_cmd": "mvn install",
            "run_cmd": "java Main",
            "test_cmd": "mvn test",
            "comment_style": "//"
        },
        "c": {
            "extensions": [".c", ".h"],
            "test_framework": "check",
            "package_file": "Makefile",
            "entry_point": "main.c",
            "docker_image": "gcc:latest",
            "install_cmd": "make",
            "run_cmd": "./main",
            "test_cmd": "make test",
            "comment_style": "//"
        },
        "cpp": {
            "extensions": [".cpp", ".hpp", ".cc", ".h"],
            "test_framework": "gtest",
            "package_file": "CMakeLists.txt",
            "entry_point": "main.cpp",
            "docker_image": "gcc:latest",
            "install_cmd": "cmake . && make",
            "run_cmd": "./main",
            "test_cmd": "make test",
            "comment_style": "//"
        }
    }
    
    @classmethod
    def get_language_config(cls, language: str) -> Optional[Dict[str, Any]]:
        """Get configuration for a language."""
        return cls.LANGUAGES.get(language.lower())
    
    @classmethod
    def detect_language(cls, code: str, filename: Optional[str] = None) -> str:
        """Detect programming language from code or filename."""
        if filename:
            ext = Path(filename).suffix
            for lang, config in cls.LANGUAGES.items():
                if ext in config["extensions"]:
                    return lang
        
        # Fallback to heuristic detection
        if "def " in code or "import " in code or "print(" in code:
            return "python"
        elif "function " in code or "const " in code or "=>" in code:
            return "javascript"
        elif "interface " in code or "type " in code or ": string" in code:
            return "typescript"
        elif "package main" in code or "func " in code:
            return "go"
        elif "fn main" in code or "use std::" in code:
            return "rust"
        elif "public static void main" in code:
            return "java"
        elif "#include" in code and "int main(" in code:
            return "c" if ".c" in (filename or "") else "cpp"
        
        return "python"  # Default


class MultiLanguageGenerator:
    """Generates code in multiple programming languages."""
    
    def __init__(self, llm_provider):
        """
        Initialize multi-language generator.
        
        Args:
            llm_provider: LLM provider for code generation
        """
        self.llm = llm_provider
        self.language_config = LanguageConfig()
        logger.info("MultiLanguageGenerator initialized")
    
    async def generate_code(
        self,
        instruction: str,
        language: str = "python",
        include_tests: bool = True,
        include_docs: bool = True
    ) -> Dict[str, Any]:
        """
        Generate code in specified language.
        
        Args:
            instruction: What to build
            language: Target language
            include_tests: Generate tests
            include_docs: Generate documentation
            
        Returns:
            Generated code and metadata
        """
        config = self.language_config.get_language_config(language)
        if not config:
            return {
                "success": False,
                "error": f"Unsupported language: {language}"
            }
        
        logger.info(f"Generating {language} code", instruction=instruction[:50])
        
        # Build language-specific prompt
        prompt = self._build_prompt(instruction, language, config, include_tests, include_docs)
        
        # Generate code using LLM
        try:
            response = await self.llm.complete(prompt)
            code = self._extract_code(response)
            
            # Generate additional files
            files = {
                config["entry_point"]: code
            }
            
            if include_tests:
                test_code = await self._generate_tests(code, language, config)
                test_file = f"test_{config['entry_point']}"
                files[test_file] = test_code
            
            if include_docs:
                readme = self._generate_readme(instruction, language, config)
                files["README.md"] = readme
            
            # Generate package file
            if language == "python":
                files["requirements.txt"] = self._generate_python_requirements(code)
            elif language in ["javascript", "typescript"]:
                files["package.json"] = self._generate_package_json(instruction, language)
            elif language == "go":
                files["go.mod"] = self._generate_go_mod(instruction)
            elif language == "rust":
                files["Cargo.toml"] = self._generate_cargo_toml(instruction)
            
            return {
                "success": True,
                "language": language,
                "files": files,
                "config": config
            }
            
        except Exception as e:
            logger.error(f"Code generation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _build_prompt(
        self,
        instruction: str,
        language: str,
        config: Dict[str, Any],
        include_tests: bool,
        include_docs: bool
    ) -> str:
        """Build language-specific prompt."""
        prompt = f"""Generate production-ready {language.upper()} code for the following task:

{instruction}

Requirements:
- Use {language} best practices and idioms
- Write clean, well-documented code
- Use {config['comment_style']} for comments
- Include proper error handling
- Make it production-ready
"""
        
        if include_tests:
            prompt += f"\n- Include {config['test_framework']} tests"
        
        if include_docs:
            prompt += "\n- Add comprehensive documentation"
        
        prompt += f"\n\nGenerate complete, working code with all necessary imports and dependencies."
        
        return prompt
    
    def _extract_code(self, response: str) -> str:
        """Extract code from LLM response."""
        # Remove markdown code blocks if present
        if "```" in response:
            parts = response.split("```")
            for part in parts:
                if any(lang in part.lower() for lang in ["python", "javascript", "typescript", "go", "rust", "java"]):
                    lines = part.split("\n")[1:]  # Skip language identifier
                    return "\n".join(lines)
            # If no language identifier, take first code block
            if len(parts) > 1:
                return parts[1]
        
        return response.strip()
    
    async def _generate_tests(
        self,
        code: str,
        language: str,
        config: Dict[str, Any]
    ) -> str:
        """Generate test code."""
        prompt = f"""Generate comprehensive {config['test_framework']} tests for this {language} code:

{code}

Generate tests that:
- Cover main functionality
- Test edge cases
- Include error handling tests
- Are production-ready
"""
        
        try:
            response = await self.llm.complete(prompt)
            return self._extract_code(response)
        except Exception as e:
            logger.error(f"Test generation failed: {e}")
            return f"{config['comment_style']} TODO: Add tests"
    
    def _generate_readme(
        self,
        instruction: str,
        language: str,
        config: Dict[str, Any]
    ) -> str:
        """Generate README documentation."""
        return f"""# {instruction.split()[0].capitalize()} Project

## Description
{instruction}

## Language
{language.capitalize()}

## Installation
```bash
{config['install_cmd']}
```

## Usage
```bash
{config['run_cmd']}
```

## Testing
```bash
{config['test_cmd']}
```

## Generated by SuperAgent
Production-ready code with multi-language support.
"""
    
    def _generate_python_requirements(self, code: str) -> str:
        """Generate requirements.txt from imports."""
        # Extract imports
        lines = code.split("\n")
        imports = [line.split()[1].split(".")[0] for line in lines if line.strip().startswith("import ")]
        imports += [line.split()[1].split(".")[0] for line in lines if line.strip().startswith("from ")]
        
        # Filter standard library
        stdlib = {"os", "sys", "json", "re", "time", "datetime", "pathlib", "typing", "asyncio"}
        external = [imp for imp in set(imports) if imp not in stdlib]
        
        return "\n".join(sorted(external)) if external else "# No external dependencies"
    
    def _generate_package_json(self, instruction: str, language: str) -> str:
        """Generate package.json for Node.js projects."""
        return f'''{{
  "name": "{instruction.split()[0].lower()}-project",
  "version": "1.0.0",
  "description": "{instruction}",
  "main": "index.{'ts' if language == 'typescript' else 'js'}",
  "scripts": {{
    "start": "node index.js",
    "test": "jest"
  }},
  "dependencies": {{}},
  "devDependencies": {{
    "jest": "^29.0.0"
    {', "typescript": "^5.0.0", "ts-node": "^10.0.0", "@types/node": "^20.0.0"' if language == 'typescript' else ''}
  }}
}}'''
    
    def _generate_go_mod(self, instruction: str) -> str:
        """Generate go.mod for Go projects."""
        module_name = instruction.split()[0].lower()
        return f"""module github.com/user/{module_name}

go 1.21

require ()
"""
    
    def _generate_cargo_toml(self, instruction: str) -> str:
        """Generate Cargo.toml for Rust projects."""
        package_name = instruction.split()[0].lower().replace(" ", "-")
        return f"""[package]
name = "{package_name}"
version = "0.1.0"
edition = "2021"

[dependencies]
"""

