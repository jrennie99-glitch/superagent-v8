"""
Project Import/Export System
Upload ZIP files and automatically scaffold to production-ready standard
"""

import os
import zipfile
import shutil
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import tempfile

class ProjectImporter:
    """Handles project import, analysis, and production scaffolding"""
    
    def __init__(self):
        self.upload_dir = Path("uploads")
        self.output_dir = Path("output_projects")
        self.upload_dir.mkdir(exist_ok=True)
        self.output_dir.mkdir(exist_ok=True)
    
    def extract_zip(self, zip_path: Path, extract_to: Path) -> bool:
        """Extract ZIP file to specified directory with comprehensive security validation"""
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                # Validate all paths to prevent Zip Slip attack (including symlinks)
                for zip_info in zip_ref.infolist():
                    member = zip_info.filename
                    
                    # Block symlinks (check external_attr for Unix symlink flag)
                    # Symlinks have mode & 0o120000 set in external_attr upper 16 bits
                    if zip_info.external_attr >> 16 & 0o120000 == 0o120000:
                        print(f"Blocked symlink: {member}")
                        return False
                    
                    # Normalize path and check for directory traversal
                    member_path = Path(extract_to) / member
                    try:
                        member_path.resolve().relative_to(extract_to.resolve())
                    except ValueError:
                        # Path escapes extraction directory
                        print(f"Blocked malicious path: {member}")
                        return False
                    
                    # Block absolute paths and path traversal
                    if Path(member).is_absolute() or '..' in Path(member).parts:
                        print(f"Blocked unsafe path: {member}")
                        return False
                
                # Safe to extract - all security checks passed
                zip_ref.extractall(extract_to)
            return True
        except Exception as e:
            print(f"Error extracting ZIP: {e}")
            return False
    
    def analyze_project_structure(self, project_path: Path) -> Dict:
        """Analyze uploaded project and detect technology stack"""
        analysis = {
            "detected_language": "unknown",
            "framework": "unknown",
            "dependencies_file": None,
            "entry_point": None,
            "has_tests": False,
            "has_docker": False,
            "has_ci": False,
            "file_count": 0,
            "total_size": 0,
            "languages": [],
            "frameworks": [],
            "recommendations": [],
            "dependency_files": []
        }
        
        files = list(project_path.rglob("*"))
        analysis["file_count"] = len([f for f in files if f.is_file()])
        analysis["total_size"] = sum(f.stat().st_size for f in files if f.is_file())
        
        # Detect ALL languages (don't stop at first match)
        detected_primary = False
        
        # Check for JavaScript/Node.js
        if (project_path / "package.json").exists():
            if not detected_primary:
                analysis["detected_language"] = "JavaScript/Node.js"
                analysis["dependencies_file"] = "package.json"
                detected_primary = True
            analysis["languages"].append("JavaScript")
            analysis["dependency_files"].append("package.json")
            
            # Check for frameworks
            try:
                with open(project_path / "package.json") as f:
                    pkg = json.load(f)
                    deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
                    
                    if "react" in deps:
                        analysis["frameworks"].append("React")
                        if not detected_primary or analysis["framework"] == "unknown":
                            analysis["framework"] = "React"
                    if "next" in deps:
                        analysis["frameworks"].append("Next.js")
                        if not detected_primary or analysis["framework"] == "unknown":
                            analysis["framework"] = "Next.js"
                    if "vue" in deps:
                        analysis["frameworks"].append("Vue.js")
                    if "express" in deps:
                        analysis["frameworks"].append("Express")
                    
                    # Detect entry point
                    if "main" in pkg:
                        analysis["entry_point"] = pkg["main"]
                    elif "scripts" in pkg and "start" in pkg["scripts"]:
                        analysis["entry_point"] = "npm start"
            except:
                pass
        
        # Check for Python
        if (project_path / "requirements.txt").exists() or (project_path / "pyproject.toml").exists():
            if not detected_primary:
                analysis["detected_language"] = "Python"
                analysis["dependencies_file"] = "requirements.txt" if (project_path / "requirements.txt").exists() else "pyproject.toml"
                detected_primary = True
            analysis["languages"].append("Python")
            if (project_path / "requirements.txt").exists():
                analysis["dependency_files"].append("requirements.txt")
            if (project_path / "pyproject.toml").exists():
                analysis["dependency_files"].append("pyproject.toml")
            
            # Detect Python frameworks
            if (project_path / "app.py").exists() or (project_path / "main.py").exists():
                analysis["entry_point"] = "app.py" if (project_path / "app.py").exists() else "main.py"
                
                # Check for Flask/FastAPI
                if (project_path / "requirements.txt").exists():
                    try:
                        with open(project_path / "requirements.txt") as f:
                            reqs = f.read().lower()
                            if "flask" in reqs:
                                analysis["frameworks"].append("Flask")
                                if analysis["framework"] == "unknown":
                                    analysis["framework"] = "Flask"
                            if "fastapi" in reqs:
                                analysis["frameworks"].append("FastAPI")
                                if analysis["framework"] == "unknown":
                                    analysis["framework"] = "FastAPI"
                            if "django" in reqs:
                                analysis["frameworks"].append("Django")
                    except:
                        pass
        
        # Check for Go
        if (project_path / "go.mod").exists():
            if not detected_primary:
                analysis["detected_language"] = "Go"
                analysis["dependencies_file"] = "go.mod"
                detected_primary = True
            analysis["languages"].append("Go")
            analysis["dependency_files"].append("go.mod")
        
        # Check for Rust
        if (project_path / "Cargo.toml").exists():
            if not detected_primary:
                analysis["detected_language"] = "Rust"
                analysis["dependencies_file"] = "Cargo.toml"
                detected_primary = True
            analysis["languages"].append("Rust")
            analysis["dependency_files"].append("Cargo.toml")
        
        # Check for PHP
        if (project_path / "composer.json").exists():
            if not detected_primary:
                analysis["detected_language"] = "PHP"
                analysis["dependencies_file"] = "composer.json"
                detected_primary = True
            analysis["languages"].append("PHP")
            analysis["dependency_files"].append("composer.json")
        
        # Check for existing production files
        analysis["has_docker"] = (project_path / "Dockerfile").exists()
        analysis["has_ci"] = (project_path / ".github" / "workflows").exists() or (project_path / ".gitlab-ci.yml").exists()
        
        # Check for tests
        test_patterns = ["test", "tests", "spec", "__tests__"]
        analysis["has_tests"] = any((project_path / pattern).exists() for pattern in test_patterns)
        
        # Smart primary language selection for mixed-language projects
        # Prioritize based on entry points rather than just first match
        if len(analysis["languages"]) > 1:
            # If Python has an entry point (app.py/main.py), it's likely the backend
            if "Python" in analysis["languages"] and analysis.get("entry_point"):
                if analysis["entry_point"] in ["app.py", "main.py"]:
                    analysis["detected_language"] = "Python"
                    # Find Python dependencies
                    for df in analysis["dependency_files"]:
                        if "requirements.txt" in str(df) or "pyproject.toml" in str(df):
                            analysis["dependencies_file"] = str(df)
                            break
            # If Node has package.json with a start script, prefer it
            elif "JavaScript" in analysis["languages"] and (project_path / "package.json").exists():
                try:
                    with open(project_path / "package.json") as f:
                        pkg = json.load(f)
                        if pkg.get("scripts", {}).get("start"):
                            analysis["detected_language"] = "JavaScript/Node.js"
                            analysis["dependencies_file"] = "package.json"
                except:
                    pass
        
        # Generate recommendations
        if not analysis["has_docker"]:
            analysis["recommendations"].append("Add Dockerfile for containerization")
        if not analysis["has_tests"]:
            analysis["recommendations"].append("Add test suite")
        if not analysis["has_ci"]:
            analysis["recommendations"].append("Add CI/CD pipeline")
        if analysis["dependencies_file"] is None:
            analysis["recommendations"].append("Add dependency management file")
        
        # Add note for mixed-language projects
        if len(analysis["languages"]) > 1:
            langs = ", ".join(analysis["languages"])
            analysis["recommendations"].append(f"Multi-language project detected ({langs}). Dockerfile targets {analysis['detected_language']}.")
        
        return analysis
    
    def scaffold_production_files(self, project_path: Path, analysis: Dict) -> List[str]:
        """Generate production-ready configuration files"""
        generated_files = []
        
        # Generate Dockerfile
        if not analysis["has_docker"]:
            dockerfile_content = self._generate_dockerfile(analysis, project_path)
            if dockerfile_content:
                with open(project_path / "Dockerfile", "w") as f:
                    f.write(dockerfile_content)
                generated_files.append("Dockerfile")
        
        # Generate .dockerignore
        if not (project_path / ".dockerignore").exists():
            dockerignore = self._generate_dockerignore(analysis)
            with open(project_path / ".dockerignore", "w") as f:
                f.write(dockerignore)
            generated_files.append(".dockerignore")
        
        # Generate README.md if missing
        if not (project_path / "README.md").exists():
            readme = self._generate_readme(analysis, project_path)
            with open(project_path / "README.md", "w") as f:
                f.write(readme)
            generated_files.append("README.md")
        
        # Generate .env.example
        if not (project_path / ".env.example").exists():
            env_example = self._generate_env_example(analysis)
            with open(project_path / ".env.example", "w") as f:
                f.write(env_example)
            generated_files.append(".env.example")
        
        # Generate .gitignore if missing
        if not (project_path / ".gitignore").exists():
            gitignore = self._generate_gitignore(analysis)
            with open(project_path / ".gitignore", "w") as f:
                f.write(gitignore)
            generated_files.append(".gitignore")
        
        # Generate GitHub Actions workflow
        if not analysis["has_ci"]:
            workflows_dir = project_path / ".github" / "workflows"
            workflows_dir.mkdir(parents=True, exist_ok=True)
            ci_workflow = self._generate_ci_workflow(analysis)
            with open(workflows_dir / "ci.yml", "w") as f:
                f.write(ci_workflow)
            generated_files.append(".github/workflows/ci.yml")
        
        # Generate deployment config
        deploy_config = self._generate_deployment_config(analysis)
        with open(project_path / "deployment.json", "w") as f:
            json.dump(deploy_config, f, indent=2)
        generated_files.append("deployment.json")
        
        return generated_files
    
    def _generate_dockerfile(self, analysis: Dict, project_path: Path = None) -> Optional[str]:
        """Generate appropriate Dockerfile based on detected language"""
        lang = analysis["detected_language"]
        
        if "Python" in lang:
            deps_file = analysis.get('dependencies_file', 'requirements.txt')
            
            # Handle pyproject.toml vs requirements.txt
            if deps_file == "pyproject.toml":
                # For pyproject.toml, copy everything and install
                entry_point = analysis.get('entry_point', 'main.py')
                return f"""# Production Dockerfile for Python
FROM python:3.11-slim

WORKDIR /app

# Copy project files
COPY . .

# Install project and dependencies
RUN pip install --no-cache-dir .

# Expose port
EXPOSE 5000

# Run application
CMD ["python", "{entry_point}"]
"""
            else:
                # For requirements.txt, use traditional approach
                return f"""# Production Dockerfile for Python
FROM python:3.11-slim

WORKDIR /app

# Copy dependencies first for layer caching
COPY {deps_file} .
RUN pip install --no-cache-dir -r {deps_file}

# Copy application
COPY . .

# Expose port
EXPOSE 5000

# Run application
CMD ["python", "{analysis.get('entry_point', 'main.py')}"]
"""
        
        elif "JavaScript" in lang or "Node" in lang:
            return """# Production Dockerfile for Node.js
FROM node:18-alpine

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm ci --only=production

# Copy application
COPY . .

# Build if needed
RUN npm run build || true

# Expose port
EXPOSE 5000

# Run application
CMD ["npm", "start"]
"""
        
        elif "Go" in lang:
            return """# Production Dockerfile for Go
FROM golang:1.21-alpine AS builder

WORKDIR /app
COPY . .
RUN go build -o main .

FROM alpine:latest
WORKDIR /app
COPY --from=builder /app/main .

EXPOSE 8080
CMD ["./main"]
"""
        
        elif "Rust" in lang:
            # Parse Cargo.toml to get package name from the uploaded project
            binary_name = "app"
            try:
                # Look for Cargo.toml in the project path
                cargo_path = None
                if project_path and (project_path / "Cargo.toml").exists():
                    cargo_path = project_path / "Cargo.toml"
                
                if cargo_path and cargo_path.exists():
                    with open(cargo_path) as f:
                        in_package = False
                        for line in f:
                            line = line.strip()
                            if line == "[package]":
                                in_package = True
                            elif line.startswith("["):
                                in_package = False
                            elif in_package and line.startswith("name"):
                                name_val = line.split("=", 1)[1].strip()
                                binary_name = name_val.strip('"').strip("'")
                                break
            except Exception as e:
                print(f"Failed to parse Cargo.toml: {e}")
                binary_name = "app"
            
            return f"""# Production Dockerfile for Rust
FROM rust:latest AS builder

WORKDIR /app
COPY . .
RUN cargo build --release

FROM debian:bookworm-slim
WORKDIR /app
RUN apt-get update && apt-get install -y ca-certificates && rm -rf /var/lib/apt/lists/*

# Copy the compiled binary
COPY --from=builder /app/target/release/{binary_name} ./app

EXPOSE 8080

# Run the application
CMD ["./app"]
"""
        
        return None
    
    def _generate_dockerignore(self, analysis: Dict) -> str:
        """Generate .dockerignore file"""
        base = """# Dependencies
node_modules/
__pycache__/
*.pyc
.venv/
venv/

# IDE
.vscode/
.idea/
*.swp

# Git
.git/
.gitignore

# CI/CD
.github/
.gitlab-ci.yml

# Docs
README.md
docs/

# Tests
tests/
test/
*.test.js
*_test.go
"""
        return base
    
    def _generate_readme(self, analysis: Dict, project_path: Path) -> str:
        """Generate comprehensive README"""
        project_name = project_path.name.replace("_", " ").title()
        
        return f"""# {project_name}

## 🚀 Quick Start

### Prerequisites
- {analysis['detected_language']}
{"- Docker (optional but recommended)" if not analysis['has_docker'] else "- Docker"}

### Installation

```bash
# Install dependencies
{self._get_install_command(analysis)}

# Run application
{self._get_run_command(analysis)}
```

### Docker Deployment

```bash
# Build image
docker build -t {project_name.lower().replace(' ', '-')} .

# Run container
docker run -p 5000:5000 {project_name.lower().replace(' ', '-')}
```

## 📋 Features

- Production-ready configuration
- Docker support
- CI/CD pipeline
- Environment variable management

## 🛠️ Technology Stack

- **Language**: {analysis['detected_language']}
{f"- **Framework**: {analysis['framework']}" if analysis['framework'] != 'unknown' else ""}

## 📝 Project Structure

```
{self._generate_tree_structure(project_path)}
```

## 🔧 Configuration

Copy `.env.example` to `.env` and configure your environment variables.

## 📦 Deployment

This project is ready for deployment to:
- Docker/Kubernetes
- Heroku
- AWS/GCP/Azure
- Vercel/Netlify (for frontend)
- Railway/Render

## 📄 License

MIT License

---

*Generated by SuperAgent - Production-Ready Scaffolding System*
"""
    
    def _get_install_command(self, analysis: Dict) -> str:
        """Get installation command based on language"""
        if "JavaScript" in analysis["detected_language"]:
            return "npm install"
        elif "Python" in analysis["detected_language"]:
            return "pip install -r requirements.txt"
        elif "Go" in analysis["detected_language"]:
            return "go mod download"
        elif "Rust" in analysis["detected_language"]:
            return "cargo build"
        return "# Install dependencies"
    
    def _get_run_command(self, analysis: Dict) -> str:
        """Get run command based on language"""
        if analysis.get("entry_point"):
            if "npm start" in str(analysis["entry_point"]):
                return "npm start"
            else:
                return f"python {analysis['entry_point']}" if "Python" in analysis["detected_language"] else f"node {analysis['entry_point']}"
        return "# Run your application"
    
    def _generate_tree_structure(self, project_path: Path) -> str:
        """Generate simple directory tree"""
        tree = []
        for item in sorted(project_path.iterdir())[:10]:  # Limit to first 10 items
            if item.name.startswith('.'):
                continue
            tree.append(f"├── {item.name}{'/' if item.is_dir() else ''}")
        return "\n".join(tree) if tree else "├── (files)"
    
    def _generate_env_example(self, analysis: Dict) -> str:
        """Generate .env.example file"""
        return """# Environment Variables
PORT=5000
NODE_ENV=production

# Database (if applicable)
# DATABASE_URL=

# API Keys
# API_KEY=

# Add your environment variables here
"""
    
    def _generate_gitignore(self, analysis: Dict) -> str:
        """Generate .gitignore file"""
        base = """# Dependencies
node_modules/
__pycache__/
*.pyc
.venv/
venv/

# Environment
.env
.env.local

# IDE
.vscode/
.idea/
*.swp

# OS
.DS_Store
Thumbs.db

# Build
dist/
build/
*.log
"""
        return base
    
    def _generate_ci_workflow(self, analysis: Dict) -> str:
        """Generate GitHub Actions CI workflow"""
        lang = analysis["detected_language"]
        
        if "Python" in lang:
            return """name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    
    - name: Run tests
      run: |
        pytest || echo "No tests found"
    
    - name: Build Docker image
      run: docker build -t app .
"""
        
        elif "JavaScript" in lang:
            return """name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'
    
    - name: Install dependencies
      run: npm ci
    
    - name: Run tests
      run: npm test || echo "No tests configured"
    
    - name: Build
      run: npm run build || echo "No build step"
    
    - name: Build Docker image
      run: docker build -t app .
"""
        
        return "# Add your CI/CD workflow here"
    
    def _generate_deployment_config(self, analysis: Dict) -> Dict:
        """Generate deployment configuration"""
        return {
            "name": "SuperAgent Project",
            "type": "docker",
            "language": analysis["detected_language"],
            "framework": analysis["framework"],
            "build": {
                "dockerfile": "Dockerfile",
                "context": "."
            },
            "deploy": {
                "port": 5000,
                "environment": "production",
                "healthCheck": "/health"
            },
            "platforms": {
                "docker": "docker build -t app .",
                "heroku": "git push heroku main",
                "railway": "railway up",
                "render": "render deploy"
            }
        }
    
    def create_output_zip(self, project_path: Path, output_name: str) -> Path:
        """Create ZIP file of processed project"""
        output_zip = self.output_dir / f"{output_name}.zip"
        
        with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in project_path.rglob('*'):
                if file_path.is_file():
                    arcname = file_path.relative_to(project_path)
                    zipf.write(file_path, arcname)
        
        return output_zip
    
    def process_upload(self, zip_file_path: str, project_name: str) -> Dict:
        """Main processing pipeline for uploaded ZIP"""
        try:
            # Create temp directory for extraction
            temp_dir = Path(tempfile.mkdtemp())
            zip_path = Path(zip_file_path)
            
            # Extract ZIP
            if not self.extract_zip(zip_path, temp_dir):
                return {"success": False, "error": "Failed to extract ZIP file"}
            
            # Find actual project root (handle nested folders)
            project_root = temp_dir
            subdirs = [d for d in temp_dir.iterdir() if d.is_dir()]
            if len(subdirs) == 1 and len(list(temp_dir.glob('*'))) == 1:
                project_root = subdirs[0]
            
            # Analyze project
            analysis = self.analyze_project_structure(project_root)
            
            # Scaffold production files
            generated_files = self.scaffold_production_files(project_root, analysis)
            
            # Create output ZIP
            output_zip = self.create_output_zip(project_root, project_name)
            
            # Cleanup temp directory
            shutil.rmtree(temp_dir, ignore_errors=True)
            
            return {
                "success": True,
                "project_name": project_name,
                "analysis": analysis,
                "generated_files": generated_files,
                "output_zip": str(output_zip),
                "download_url": f"/api/v1/project/download/{project_name}.zip"
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


# Global instance
project_importer = ProjectImporter()
