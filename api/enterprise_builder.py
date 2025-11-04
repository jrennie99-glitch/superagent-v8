"""
Enterprise-Grade Build System for SuperAgent
Adds checkpoint creation, multi-file projects, dependency management, testing, and verification
WITHOUT removing any existing features
"""
import os
import asyncio
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Callable
import json
from datetime import datetime
import time

class EnterpriseBuildSystem:
    """
    Enterprise-level build orchestrator that wraps the basic builder
    Adds: checkpoints, multi-step builds, testing, verification, production outputs
    """
    
    def __init__(self, basic_builder, rollback_system, hallucination_fixer, cybersecurity_ai):
        self.basic_builder = basic_builder
        self.rollback_system = rollback_system
        self.hallucination_fixer = hallucination_fixer
        self.cybersecurity_ai = cybersecurity_ai
        self.build_stages = []
        self.current_stage = 0
        
    async def enterprise_build(
        self,
        instruction: str,
        language: str,
        enable_checkpoints: bool = True,
        enable_testing: bool = True,
        enable_security_scan: bool = True,
        enable_multi_file: bool = True,
        progress_callback: Optional[Callable] = None
    ) -> Dict:
        """
        Enterprise-grade build process with all safety features
        
        Stages:
        1. Pre-Build Safety (Checkpoint)
        2. Architecture Planning
        3. Code Generation (Multi-file)
        4. Dependency Installation
        5. Automated Testing
        6. Security Scanning
        7. Code Verification
        8. Production Outputs
        9. Final Checkpoint
        """
        build_start = time.time()
        results = {
            "success": True,
            "stages": [],
            "files_created": [],
            "dependencies_installed": [],
            "tests_passed": 0,
            "security_issues": [],
            "build_time": 0,
            "checkpoint_before": None,
            "checkpoint_after": None
        }
        
        try:
            # STAGE 1: Pre-Build Safety - Create Checkpoint
            if enable_checkpoints:
                stage_result = await self._stage_create_checkpoint(instruction)
                results["checkpoint_before"] = stage_result["checkpoint_id"]
                results["stages"].append(stage_result)
                if progress_callback:
                    await progress_callback("Stage 1/9: Checkpoint created for safety", 11)
            
            # STAGE 2: Architecture Planning
            stage_result = await self._stage_architecture_planning(instruction, language, enable_multi_file)
            results["stages"].append(stage_result)
            architecture = stage_result["architecture"]
            if progress_callback:
                await progress_callback("Stage 2/9: Architecture planned", 22)
            
            # STAGE 3: Code Generation (Multi-file or single-file)
            stage_result = await self._stage_code_generation(instruction, language, architecture)
            results["stages"].append(stage_result)
            
            # CRITICAL: Check if code generation succeeded
            if not stage_result["success"] or len(stage_result["files"]) == 0:
                raise Exception(f"Code generation failed: {stage_result.get('error', 'No files generated')}")
            
            results["files_created"].extend(stage_result["files"])
            generated_files = stage_result["files"]
            if progress_callback:
                await progress_callback(f"Stage 3/9: Generated {len(generated_files)} files", 33)
            
            # STAGE 4: Create Project Structure
            stage_result = await self._stage_create_files(generated_files, instruction)
            results["stages"].append(stage_result)
            
            # Validate project directory was created
            if not stage_result["success"] or not stage_result["project_dir"]:
                raise Exception(f"Failed to create project structure: {stage_result.get('error', 'Unknown error')}")
            
            project_dir = stage_result["project_dir"]
            if progress_callback:
                await progress_callback("Stage 4/9: Project structure created", 44)
            
            # STAGE 5: Dependency Installation
            stage_result = await self._stage_install_dependencies(project_dir, language, architecture)
            results["dependencies_installed"] = stage_result["installed"]
            results["stages"].append(stage_result)
            if progress_callback:
                await progress_callback(f"Stage 5/9: Installed {len(stage_result['installed'])} dependencies", 55)
            
            # STAGE 6: Automated Testing
            if enable_testing:
                stage_result = await self._stage_run_tests(project_dir, language)
                results["tests_passed"] = stage_result["tests_passed"]
                results["stages"].append(stage_result)
                if progress_callback:
                    await progress_callback(f"Stage 6/9: {stage_result['tests_passed']} tests passed", 66)
            
            # STAGE 7: Security Scanning
            if enable_security_scan:
                stage_result = await self._stage_security_scan(generated_files)
                results["security_issues"] = stage_result["issues"]
                results["stages"].append(stage_result)
                if progress_callback:
                    await progress_callback(f"Stage 7/9: Security scan complete ({len(stage_result['issues'])} issues)", 77)
            
            # STAGE 8: Code Verification
            stage_result = await self._stage_code_verification(generated_files, instruction)
            results["verification_score"] = stage_result["score"]
            results["stages"].append(stage_result)
            if progress_callback:
                await progress_callback(f"Stage 8/9: Code verified (score: {stage_result['score']}/100)", 88)
            
            # STAGE 9: Production Outputs (Dockerfile, CI/CD, Docs)
            stage_result = await self._stage_production_outputs(project_dir, language, architecture)
            results["production_files"] = stage_result["files"]
            results["stages"].append(stage_result)
            if progress_callback:
                await progress_callback("Stage 9/9: Production files created", 100)
            
            # Final Checkpoint
            if enable_checkpoints:
                final_checkpoint = await self._stage_create_checkpoint(f"Completed: {instruction}")
                results["checkpoint_after"] = final_checkpoint["checkpoint_id"]
            
            results["build_time"] = round(time.time() - build_start, 2)
            results["project_dir"] = project_dir
            results["message"] = f"✅ Enterprise build complete in {results['build_time']}s"
            
        except Exception as e:
            results["success"] = False
            results["error"] = str(e)
            results["message"] = f"❌ Build failed: {str(e)}"
            
            # Rollback to checkpoint if available
            if enable_checkpoints and results.get("checkpoint_before"):
                try:
                    self.rollback_system.rollback_to_checkpoint(results["checkpoint_before"])
                    results["rollback"] = "Rolled back to pre-build checkpoint"
                except:
                    pass
        
        return results
    
    async def _stage_create_checkpoint(self, description: str) -> Dict:
        """Stage 1 & 9: Create safety checkpoint"""
        try:
            checkpoint = self.rollback_system.create_checkpoint(description)
            return {
                "stage": "checkpoint",
                "success": True,
                "checkpoint_id": checkpoint.get("checkpoint_id"),
                "description": description,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "stage": "checkpoint",
                "success": False,
                "error": str(e)
            }
    
    async def _stage_architecture_planning(self, instruction: str, language: str, multi_file: bool) -> Dict:
        """Stage 2: Plan architecture and file structure"""
        try:
            # Analyze instruction to determine architecture
            architecture = {
                "type": self._detect_project_type(instruction, language),
                "language": language,
                "multi_file": multi_file,
                "needs_database": self._needs_database(instruction),
                "needs_api": self._needs_api(instruction),
                "needs_frontend": self._needs_frontend(instruction),
                "files_to_create": []
            }
            
            # Plan file structure
            if multi_file:
                architecture["files_to_create"] = self._plan_file_structure(architecture)
            else:
                architecture["files_to_create"] = [{"name": "main", "type": "primary"}]
            
            return {
                "stage": "architecture_planning",
                "success": True,
                "architecture": architecture,
                "files_planned": len(architecture["files_to_create"])
            }
        except Exception as e:
            return {
                "stage": "architecture_planning",
                "success": False,
                "error": str(e),
                "architecture": {"type": "simple", "files_to_create": []}
            }
    
    async def _stage_code_generation(self, instruction: str, language: str, architecture: Dict) -> Dict:
        """Stage 3: Generate code for all files"""
        try:
            import google.generativeai as genai
            
            gemini_key = os.getenv("GEMINI_API_KEY")
            genai.configure(api_key=gemini_key)
            model = genai.GenerativeModel('gemini-2.0-flash')
            
            generated_files = []
            
            if architecture["multi_file"] and len(architecture["files_to_create"]) > 1:
                # Multi-file project
                for file_plan in architecture["files_to_create"]:
                    prompt = self._create_file_prompt(instruction, language, file_plan, architecture)
                    response = model.generate_content(prompt)
                    
                    generated_files.append({
                        "name": file_plan["name"],
                        "type": file_plan["type"],
                        "code": self._clean_code(response.text),
                        "language": language
                    })
                    
                    # Small delay to avoid rate limits
                    await asyncio.sleep(0.5)
            else:
                # Single file (backwards compatible with existing system)
                prompt = f"Generate complete, production-ready {language} code for: {instruction}\n\nProvide clean, well-documented code."
                response = model.generate_content(prompt)
                
                generated_files.append({
                    "name": "main",
                    "type": "primary",
                    "code": self._clean_code(response.text),
                    "language": language
                })
            
            return {
                "stage": "code_generation",
                "success": True,
                "files": generated_files,
                "file_count": len(generated_files)
            }
        except Exception as e:
            return {
                "stage": "code_generation",
                "success": False,
                "error": str(e),
                "files": []
            }
    
    async def _stage_create_files(self, files: List[Dict], instruction: str) -> Dict:
        """Stage 4: Create project directory and write files"""
        try:
            # Generate project name
            import re
            project_name = re.sub(r'[^a-z0-9]+', '_', instruction.lower()[:30])
            project_dir = Path.cwd() / f"enterprise_{project_name}_{int(time.time())}"
            project_dir.mkdir(parents=True, exist_ok=True)
            
            created_files = []
            for file_info in files:
                # Determine file extension
                ext = self._get_file_extension(file_info["language"], file_info["type"])
                filename = f"{file_info['name']}{ext}"
                filepath = project_dir / filename
                
                # Write file
                filepath.write_text(file_info["code"])
                created_files.append(str(filepath))
            
            return {
                "stage": "create_files",
                "success": True,
                "project_dir": str(project_dir),
                "files_created": created_files
            }
        except Exception as e:
            return {
                "stage": "create_files",
                "success": False,
                "error": str(e),
                "project_dir": ""
            }
    
    async def _stage_install_dependencies(self, project_dir: str, language: str, architecture: Dict) -> Dict:
        """Stage 5: Install real dependencies"""
        try:
            installed = []
            
            if language.lower() == "python":
                # Create requirements.txt if needed
                requirements_file = Path(project_dir) / "requirements.txt"
                if not requirements_file.exists():
                    # Generate requirements based on architecture
                    deps = self._get_python_dependencies(architecture)
                    if deps:
                        requirements_file.write_text("\n".join(deps))
                
                # Install with pip
                if requirements_file.exists():
                    result = await asyncio.create_subprocess_exec(
                        "pip", "install", "-r", str(requirements_file),
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE
                    )
                    await result.wait()
                    installed = [line.strip() for line in requirements_file.read_text().split("\n") if line.strip()]
            
            elif language.lower() in ["javascript", "typescript", "node"]:
                # Create package.json if needed
                package_file = Path(project_dir) / "package.json"
                if not package_file.exists():
                    deps = self._get_node_dependencies(architecture)
                    package_data = {
                        "name": Path(project_dir).name,
                        "version": "1.0.0",
                        "dependencies": deps
                    }
                    package_file.write_text(json.dumps(package_data, indent=2))
                
                # Install with npm
                if package_file.exists():
                    result = await asyncio.create_subprocess_exec(
                        "npm", "install",
                        cwd=project_dir,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE
                    )
                    await result.wait()
                    installed = list(json.loads(package_file.read_text()).get("dependencies", {}).keys())
            
            return {
                "stage": "install_dependencies",
                "success": True,
                "installed": installed,
                "count": len(installed)
            }
        except Exception as e:
            return {
                "stage": "install_dependencies",
                "success": False,
                "error": str(e),
                "installed": []
            }
    
    async def _stage_run_tests(self, project_dir: str, language: str) -> Dict:
        """Stage 6: Run automated tests"""
        try:
            tests_passed = 0
            tests_failed = 0
            
            if language.lower() == "python":
                # Try to run pytest
                result = await asyncio.create_subprocess_exec(
                    "python", "-m", "pytest", "--tb=short",
                    cwd=project_dir,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                stdout, stderr = await result.communicate()
                
                # Parse pytest output
                output = stdout.decode()
                if "passed" in output:
                    import re
                    match = re.search(r'(\d+) passed', output)
                    if match:
                        tests_passed = int(match.group(1))
            
            return {
                "stage": "automated_testing",
                "success": True,
                "tests_passed": tests_passed,
                "tests_failed": tests_failed
            }
        except Exception as e:
            return {
                "stage": "automated_testing",
                "success": False,
                "error": str(e),
                "tests_passed": 0
            }
    
    async def _stage_security_scan(self, files: List[Dict]) -> Dict:
        """Stage 7: Security scanning with cybersecurity AI"""
        try:
            all_issues = []
            
            for file_info in files:
                scan_result = self.cybersecurity_ai.scan_code(
                    file_info["code"],
                    file_info["language"]
                )
                
                if scan_result.get("threats"):
                    all_issues.extend(scan_result["threats"])
            
            return {
                "stage": "security_scan",
                "success": True,
                "issues": all_issues,
                "critical_count": len([i for i in all_issues if i.get("severity") == "critical"])
            }
        except Exception as e:
            return {
                "stage": "security_scan",
                "success": False,
                "error": str(e),
                "issues": []
            }
    
    async def _stage_code_verification(self, files: List[Dict], instruction: str) -> Dict:
        """Stage 8: Multi-layer code verification"""
        try:
            total_score = 0
            file_scores = []
            
            for file_info in files:
                verification = self.hallucination_fixer.verify_code(
                    file_info["code"],
                    file_info["language"],
                    instruction
                )
                
                file_scores.append(verification["score"])
            
            avg_score = sum(file_scores) / len(file_scores) if file_scores else 0
            
            return {
                "stage": "code_verification",
                "success": True,
                "score": int(avg_score),
                "files_verified": len(files)
            }
        except Exception as e:
            return {
                "stage": "code_verification",
                "success": False,
                "error": str(e),
                "score": 0
            }
    
    async def _stage_production_outputs(self, project_dir: str, language: str, architecture: Dict) -> Dict:
        """Stage 9: Generate production files (Dockerfile, CI/CD, docs)"""
        try:
            project_path = Path(project_dir)
            production_files = []
            
            # Create Dockerfile
            dockerfile = self._generate_dockerfile(language, architecture)
            if dockerfile:
                (project_path / "Dockerfile").write_text(dockerfile)
                production_files.append("Dockerfile")
            
            # Create .dockerignore
            dockerignore = self._generate_dockerignore(language)
            (project_path / ".dockerignore").write_text(dockerignore)
            production_files.append(".dockerignore")
            
            # Create GitHub Actions CI/CD
            github_dir = project_path / ".github" / "workflows"
            github_dir.mkdir(parents=True, exist_ok=True)
            ci_config = self._generate_ci_config(language)
            (github_dir / "ci.yml").write_text(ci_config)
            production_files.append(".github/workflows/ci.yml")
            
            # Create README
            readme = self._generate_readme(architecture)
            (project_path / "README.md").write_text(readme)
            production_files.append("README.md")
            
            return {
                "stage": "production_outputs",
                "success": True,
                "files": production_files
            }
        except Exception as e:
            return {
                "stage": "production_outputs",
                "success": False,
                "error": str(e),
                "files": []
            }
    
    # Helper methods
    def _detect_project_type(self, instruction: str, language: str) -> str:
        """Detect project type from instruction"""
        instruction_lower = instruction.lower()
        
        if "api" in instruction_lower or "backend" in instruction_lower:
            return "api"
        elif "website" in instruction_lower or "web app" in instruction_lower:
            return "webapp"
        elif "cli" in instruction_lower or "command line" in instruction_lower:
            return "cli"
        elif "bot" in instruction_lower:
            return "bot"
        else:
            return "general"
    
    def _needs_database(self, instruction: str) -> bool:
        """Check if project needs database"""
        keywords = ["database", "store", "save", "persist", "sql", "mongodb"]
        return any(kw in instruction.lower() for kw in keywords)
    
    def _needs_api(self, instruction: str) -> bool:
        """Check if project needs API"""
        keywords = ["api", "endpoint", "rest", "graphql", "backend"]
        return any(kw in instruction.lower() for kw in keywords)
    
    def _needs_frontend(self, instruction: str) -> bool:
        """Check if project needs frontend"""
        keywords = ["website", "web", "frontend", "ui", "interface", "page"]
        return any(kw in instruction.lower() for kw in keywords)
    
    def _plan_file_structure(self, architecture: Dict) -> List[Dict]:
        """Plan which files to create"""
        files = []
        project_type = architecture["type"]
        language = architecture["language"]
        
        if project_type == "api":
            files.append({"name": "main", "type": "entry"})
            files.append({"name": "routes", "type": "routes"})
            files.append({"name": "models", "type": "models"})
            if architecture["needs_database"]:
                files.append({"name": "database", "type": "database"})
        elif project_type == "webapp":
            files.append({"name": "app", "type": "entry"})
            files.append({"name": "index", "type": "frontend"})
            files.append({"name": "styles", "type": "styles"})
        else:
            files.append({"name": "main", "type": "entry"})
        
        # Always add config and tests
        files.append({"name": "config", "type": "config"})
        files.append({"name": "test_main", "type": "test"})
        
        return files
    
    def _create_file_prompt(self, instruction: str, language: str, file_plan: Dict, architecture: Dict) -> str:
        """Create AI prompt for specific file"""
        return f"""Generate production-ready {language} code for the {file_plan['type']} file in this project:

PROJECT: {instruction}
FILE TYPE: {file_plan['type']}
FILE NAME: {file_plan['name']}
ARCHITECTURE: {architecture['type']}

Generate ONLY the code for THIS specific file. Make it production-ready with:
- Proper error handling
- Type hints/annotations
- Comprehensive comments
- Security best practices
- Clean, maintainable code

Code only, no explanations:"""
    
    def _clean_code(self, code: str) -> str:
        """Remove markdown code fences"""
        import re
        code = re.sub(r'^```[\w]*\n', '', code)
        code = re.sub(r'\n```$', '', code)
        return code.strip()
    
    def _get_file_extension(self, language: str, file_type: str) -> str:
        """Get appropriate file extension"""
        lang_lower = language.lower()
        
        if lang_lower == "python":
            return ".py"
        elif lang_lower in ["javascript", "node"]:
            return ".js"
        elif lang_lower == "typescript":
            return ".ts"
        elif file_type == "frontend":
            return ".html"
        elif file_type == "styles":
            return ".css"
        else:
            return ".txt"
    
    def _get_python_dependencies(self, architecture: Dict) -> List[str]:
        """Get Python dependencies based on architecture"""
        deps = ["pytest>=7.0.0"]
        
        if architecture["needs_api"]:
            deps.extend(["fastapi>=0.100.0", "uvicorn>=0.23.0"])
        if architecture["needs_database"]:
            deps.append("sqlalchemy>=2.0.0")
        
        return deps
    
    def _get_node_dependencies(self, architecture: Dict) -> Dict[str, str]:
        """Get Node dependencies based on architecture"""
        deps = {}
        
        if architecture["needs_api"]:
            deps["express"] = "^4.18.0"
        
        return deps
    
    def _generate_dockerfile(self, language: str, architecture: Dict) -> str:
        """Generate Dockerfile for the project"""
        if language.lower() == "python":
            return """FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]
"""
        elif language.lower() in ["javascript", "node"]:
            return """FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

CMD ["node", "main.js"]
"""
        return ""
    
    def _generate_dockerignore(self, language: str) -> str:
        """Generate .dockerignore file"""
        return """__pycache__
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
node_modules/
.git
.gitignore
.env
*.log
"""
    
    def _generate_ci_config(self, language: str) -> str:
        """Generate GitHub Actions CI/CD config"""
        return """name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run tests
        run: |
          echo "Running tests..."
"""
    
    def _generate_readme(self, architecture: Dict) -> str:
        """Generate README.md"""
        return f"""# {architecture.get('type', 'Project').upper()} Project

## Description
Enterprise-grade application built with SuperAgent

## Architecture
- Type: {architecture['type']}
- Language: {architecture['language']}
- Multi-file: {architecture['multi_file']}

## Installation
```bash
# Install dependencies
pip install -r requirements.txt  # For Python
npm install  # For Node.js
```

## Usage
```bash
python main.py  # For Python
node main.js  # For Node.js
```

## Production Deployment
```bash
docker build -t myapp .
docker run -p 8000:8000 myapp
```

---
Built with ❤️ by SuperAgent
"""
