"""
AI-Powered Codebase Query Engine
Semantic code search with architecture understanding
"""

import os
import re
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

class CodebaseQueryEngine:
    """Semantic codebase search and analysis"""
    
    def __init__(self):
        self.indexed_files = {}
        self.query_history = []
        self.ai_provider = None
        
    def index_codebase(self, directory: str = ".") -> Dict[str, Any]:
        """Index codebase for semantic search"""
        indexed = {
            "files": [],
            "functions": [],
            "classes": [],
            "imports": [],
            "total_lines": 0
        }
        
        try:
            for root, dirs, files in os.walk(directory):
                # Skip common directories
                dirs[:] = [d for d in dirs if d not in ['.git', 'node_modules', '__pycache__', 'venv', '.pythonlibs']]
                
                for file in files:
                    if self._is_code_file(file):
                        filepath = os.path.join(root, file)
                        file_data = self._analyze_file(filepath)
                        
                        indexed["files"].append(file_data)
                        indexed["functions"].extend(file_data.get("functions", []))
                        indexed["classes"].extend(file_data.get("classes", []))
                        indexed["imports"].extend(file_data.get("imports", []))
                        indexed["total_lines"] += file_data.get("lines", 0)
            
            self.indexed_files = indexed
            return {
                "success": True,
                "files_indexed": len(indexed["files"]),
                "functions_found": len(indexed["functions"]),
                "classes_found": len(indexed["classes"]),
                "total_lines": indexed["total_lines"]
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def semantic_search(self, query: str) -> Dict[str, Any]:
        """Perform semantic search on codebase"""
        # If not indexed, index first
        if not self.indexed_files:
            self.index_codebase()
        
        results = {
            "query": query,
            "matches": [],
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Keyword-based search (enhanced)
        query_lower = query.lower()
        
        # Search in files
        for file_data in self.indexed_files.get("files", []):
            score = 0
            matched_items = []
            
            # Check filename
            if query_lower in file_data["path"].lower():
                score += 10
                matched_items.append("filename")
            
            # Check functions
            for func in file_data.get("functions", []):
                if query_lower in func.lower():
                    score += 5
                    matched_items.append(f"function: {func}")
            
            # Check classes
            for cls in file_data.get("classes", []):
                if query_lower in cls.lower():
                    score += 5
                    matched_items.append(f"class: {cls}")
            
            # Check imports
            for imp in file_data.get("imports", []):
                if query_lower in imp.lower():
                    score += 3
                    matched_items.append(f"import: {imp}")
            
            if score > 0:
                results["matches"].append({
                    "file": file_data["path"],
                    "score": score,
                    "matched_items": matched_items,
                    "language": file_data["language"]
                })
        
        # Sort by score
        results["matches"] = sorted(results["matches"], key=lambda x: x["score"], reverse=True)
        results["total_matches"] = len(results["matches"])
        
        self.query_history.append(results)
        return results
    
    def analyze_architecture(self) -> Dict[str, Any]:
        """Analyze codebase architecture"""
        if not self.indexed_files:
            self.index_codebase()
        
        # Detect patterns
        languages = {}
        for file_data in self.indexed_files.get("files", []):
            lang = file_data["language"]
            languages[lang] = languages.get(lang, 0) + 1
        
        # Detect frameworks
        frameworks = self._detect_frameworks()
        
        # Detect architecture patterns
        patterns = self._detect_patterns()
        
        return {
            "languages": languages,
            "primary_language": max(languages.items(), key=lambda x: x[1])[0] if languages else "unknown",
            "frameworks": frameworks,
            "patterns": patterns,
            "total_files": len(self.indexed_files.get("files", [])),
            "total_functions": len(self.indexed_files.get("functions", [])),
            "total_classes": len(self.indexed_files.get("classes", [])),
            "complexity": self._calculate_complexity()
        }
    
    def find_dependencies(self, component: str) -> Dict[str, Any]:
        """Find dependencies for a specific component"""
        if not self.indexed_files:
            self.index_codebase()
        
        dependencies = {
            "component": component,
            "depends_on": [],
            "depended_by": []
        }
        
        # Search for imports and references
        component_lower = component.lower()
        
        for file_data in self.indexed_files.get("files", []):
            # Check if file imports the component
            for imp in file_data.get("imports", []):
                if component_lower in imp.lower():
                    dependencies["depends_on"].append({
                        "file": file_data["path"],
                        "import": imp
                    })
        
        return dependencies
    
    def _is_code_file(self, filename: str) -> bool:
        """Check if file is a code file"""
        code_extensions = ['.py', '.js', '.ts', '.jsx', '.tsx', '.go', '.rs', '.java', '.c', '.cpp', '.h']
        return any(filename.endswith(ext) for ext in code_extensions)
    
    def _analyze_file(self, filepath: str) -> Dict[str, Any]:
        """Analyze a single file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Detect language
            ext = os.path.splitext(filepath)[1]
            language_map = {
                '.py': 'python',
                '.js': 'javascript',
                '.ts': 'typescript',
                '.jsx': 'javascript',
                '.tsx': 'typescript',
                '.go': 'go',
                '.rs': 'rust',
                '.java': 'java',
                '.c': 'c',
                '.cpp': 'cpp'
            }
            language = language_map.get(ext, 'unknown')
            
            return {
                "path": filepath,
                "language": language,
                "lines": len(content.split('\n')),
                "functions": self._extract_functions(content, language),
                "classes": self._extract_classes(content, language),
                "imports": self._extract_imports(content, language)
            }
        except Exception as e:
            return {
                "path": filepath,
                "error": str(e)
            }
    
    def _extract_functions(self, content: str, language: str) -> List[str]:
        """Extract function names"""
        functions = []
        
        if language == "python":
            functions = re.findall(r'def\s+(\w+)\s*\(', content)
        elif language in ["javascript", "typescript"]:
            functions = re.findall(r'function\s+(\w+)\s*\(', content)
            functions.extend(re.findall(r'const\s+(\w+)\s*=\s*\(.*\)\s*=>', content))
        
        return functions
    
    def _extract_classes(self, content: str, language: str) -> List[str]:
        """Extract class names"""
        classes = []
        
        if language == "python":
            classes = re.findall(r'class\s+(\w+)', content)
        elif language in ["javascript", "typescript"]:
            classes = re.findall(r'class\s+(\w+)', content)
        elif language == "java":
            classes = re.findall(r'class\s+(\w+)', content)
        
        return classes
    
    def _extract_imports(self, content: str, language: str) -> List[str]:
        """Extract import statements"""
        imports = []
        
        if language == "python":
            imports = re.findall(r'import\s+(\S+)', content)
            imports.extend(re.findall(r'from\s+(\S+)\s+import', content))
        elif language in ["javascript", "typescript"]:
            imports = re.findall(r'import\s+.*from\s+[\'"](.+?)[\'"]', content)
        
        return imports
    
    def _detect_frameworks(self) -> List[str]:
        """Detect frameworks used in codebase"""
        frameworks = []
        all_imports = self.indexed_files.get("imports", [])
        
        framework_patterns = {
            "FastAPI": ["fastapi"],
            "Flask": ["flask"],
            "Django": ["django"],
            "React": ["react"],
            "Vue": ["vue"],
            "Express": ["express"],
            "Next.js": ["next"]
        }
        
        for framework, patterns in framework_patterns.items():
            for pattern in patterns:
                if any(pattern in imp.lower() for imp in all_imports):
                    frameworks.append(framework)
                    break
        
        return frameworks
    
    def _detect_patterns(self) -> List[str]:
        """Detect architecture patterns"""
        patterns = []
        
        # Check for common patterns
        if any("controller" in f["path"].lower() for f in self.indexed_files.get("files", [])):
            patterns.append("MVC")
        
        if any("api" in f["path"].lower() for f in self.indexed_files.get("files", [])):
            patterns.append("REST API")
        
        if any("service" in f["path"].lower() for f in self.indexed_files.get("files", [])):
            patterns.append("Service Layer")
        
        return patterns
    
    def _calculate_complexity(self) -> str:
        """Calculate codebase complexity"""
        total_files = len(self.indexed_files.get("files", []))
        total_functions = len(self.indexed_files.get("functions", []))
        
        if total_files < 10:
            return "simple"
        elif total_files < 50:
            return "moderate"
        else:
            return "complex"
    
    def get_query_stats(self) -> Dict[str, Any]:
        """Get query statistics"""
        return {
            "total_queries": len(self.query_history),
            "indexed_files": len(self.indexed_files.get("files", [])),
            "recent_queries": [q["query"] for q in self.query_history[-5:]]
        }

# Global instance
codebase_query_engine = CodebaseQueryEngine()
