"""Natural language codebase querying system."""

import ast
from pathlib import Path
from typing import Dict, Any, List, Optional
import structlog

logger = structlog.get_logger()


class CodebaseQueryEngine:
    """
    Natural language interface to understand and query codebases.
    
    Features:
    - "Where is X implemented?"
    - "How does Y work?"
    - "Find all usages of Z"
    - "What does this function do?"
    - Code navigation and understanding
    """
    
    def __init__(self, llm_provider, cache_manager):
        """Initialize query engine.
        
        Args:
            llm_provider: LLM provider
            cache_manager: Cache manager
        """
        self.llm = llm_provider
        self.cache = cache_manager
        self.index = {}  # Code index
    
    async def index_codebase(self, project_path: Path):
        """Index a codebase for querying.
        
        Args:
            project_path: Path to project
        """
        logger.info(f"Indexing codebase: {project_path}")
        
        self.index = {
            "classes": {},
            "functions": {},
            "imports": {},
            "files": {}
        }
        
        py_files = list(project_path.rglob("*.py"))
        
        for file_path in py_files:
            try:
                code = file_path.read_text()
                tree = ast.parse(code)
                
                rel_path = str(file_path.relative_to(project_path))
                
                # Index classes
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        self.index["classes"][node.name] = {
                            "file": rel_path,
                            "line": node.lineno,
                            "docstring": ast.get_docstring(node),
                            "methods": [m.name for m in node.body if isinstance(m, ast.FunctionDef)]
                        }
                    
                    elif isinstance(node, ast.FunctionDef):
                        self.index["functions"][node.name] = {
                            "file": rel_path,
                            "line": node.lineno,
                            "docstring": ast.get_docstring(node),
                            "parameters": [arg.arg for arg in node.args.args]
                        }
                    
                    elif isinstance(node, ast.Import):
                        for alias in node.names:
                            self.index["imports"][alias.name] = rel_path
                
                # Store file info
                self.index["files"][rel_path] = {
                    "lines": len(code.split('\n')),
                    "size": len(code)
                }
            
            except Exception as e:
                logger.error(f"Failed to index {file_path}: {e}")
        
        logger.info(f"Indexed {len(self.index['classes'])} classes, {len(self.index['functions'])} functions")
    
    async def query(self, question: str, project_path: Optional[Path] = None) -> Dict[str, Any]:
        """Answer a question about the codebase.
        
        Args:
            question: Natural language question
            project_path: Optional project path for context
            
        Returns:
            Answer with code references
        """
        logger.info(f"Query: {question}")
        
        # Check cache
        cache_key = f"query:{question}"
        cached = await self.cache.get(cache_key)
        if cached:
            return cached
        
        # Determine query type
        query_type = self._classify_query(question)
        
        # Search index
        relevant_code = self._search_index(question, query_type)
        
        # Generate answer with AI
        answer = await self._generate_answer(question, relevant_code, query_type)
        
        # Cache result
        await self.cache.set(cache_key, answer)
        
        return answer
    
    def _classify_query(self, question: str) -> str:
        """Classify the type of query.
        
        Args:
            question: Question text
            
        Returns:
            Query type
        """
        question_lower = question.lower()
        
        if any(word in question_lower for word in ["where", "find", "locate"]):
            return "location"
        elif any(word in question_lower for word in ["how", "explain", "what does"]):
            return "explanation"
        elif any(word in question_lower for word in ["usage", "used", "called"]):
            return "usage"
        elif any(word in question_lower for word in ["implement", "work"]):
            return "implementation"
        else:
            return "general"
    
    def _search_index(self, question: str, query_type: str) -> List[Dict[str, Any]]:
        """Search code index for relevant entries.
        
        Args:
            question: Question text
            query_type: Type of query
            
        Returns:
            Relevant code entries
        """
        results = []
        
        # Extract potential identifiers from question
        words = question.split()
        
        for word in words:
            word_clean = word.strip("?.,!\"'")
            
            # Search classes
            if word_clean in self.index.get("classes", {}):
                results.append({
                    "type": "class",
                    "name": word_clean,
                    **self.index["classes"][word_clean]
                })
            
            # Search functions
            if word_clean in self.index.get("functions", {}):
                results.append({
                    "type": "function",
                    "name": word_clean,
                    **self.index["functions"][word_clean]
                })
        
        return results[:5]  # Top 5 results
    
    async def _generate_answer(self, question: str, relevant_code: List[Dict[str, Any]], 
                               query_type: str) -> Dict[str, Any]:
        """Generate answer using AI with code context.
        
        Args:
            question: Question text
            relevant_code: Relevant code entries
            query_type: Query type
            
        Returns:
            Answer with references
        """
        context = self._format_code_context(relevant_code)
        
        prompt = f"""Answer this question about the codebase:

Question: {question}

Relevant code context:
{context}

Provide a clear, concise answer with:
1. Direct answer to the question
2. Code references (file and line numbers)
3. Brief explanation if needed
4. Related code you might want to look at

Format as JSON: {{
    "answer": "...",
    "references": [{{"file": "...", "line": N, "description": "..."}}],
    "related": ["..."]
}}"""
        
        try:
            result = await self.llm.generate_structured(
                prompt,
                schema={
                    "answer": "string",
                    "references": [{"file": "string", "line": "number", "description": "string"}],
                    "related": ["string"]
                }
            )
            
            return {
                "question": question,
                "answer": result.get("answer", "No answer found"),
                "references": result.get("references", []),
                "related": result.get("related", []),
                "query_type": query_type
            }
        except Exception as e:
            logger.error(f"Answer generation failed: {e}")
            return {
                "question": question,
                "answer": "Sorry, I couldn't generate an answer.",
                "error": str(e)
            }
    
    def _format_code_context(self, relevant_code: List[Dict[str, Any]]) -> str:
        """Format code context for AI.
        
        Args:
            relevant_code: Relevant code entries
            
        Returns:
            Formatted context
        """
        lines = []
        
        for entry in relevant_code:
            lines.append(f"\n{entry['type'].upper()}: {entry['name']}")
            lines.append(f"  File: {entry['file']}:{entry['line']}")
            if entry.get('docstring'):
                lines.append(f"  Description: {entry['docstring'][:200]}")
            if entry.get('methods'):
                lines.append(f"  Methods: {', '.join(entry['methods'][:5])}")
            if entry.get('parameters'):
                lines.append(f"  Parameters: {', '.join(entry['parameters'])}")
        
        return "\n".join(lines) if lines else "No relevant code found"
    
    async def find_usages(self, symbol: str, project_path: Path) -> List[Dict[str, Any]]:
        """Find all usages of a symbol.
        
        Args:
            symbol: Symbol name to find
            project_path: Project path
            
        Returns:
            List of usages
        """
        usages = []
        
        py_files = list(project_path.rglob("*.py"))
        
        for file_path in py_files:
            try:
                code = file_path.read_text()
                lines = code.split('\n')
                
                for i, line in enumerate(lines, 1):
                    if symbol in line:
                        usages.append({
                            "file": str(file_path.relative_to(project_path)),
                            "line": i,
                            "content": line.strip()
                        })
            except:
                pass
        
        return usages
    
    async def explain_code(self, code_snippet: str) -> str:
        """Explain what a code snippet does.
        
        Args:
            code_snippet: Code to explain
            
        Returns:
            Explanation
        """
        prompt = f"""Explain what this code does in simple terms:

{code_snippet}

Provide:
1. High-level purpose
2. Step-by-step breakdown
3. Key concepts used
4. Potential issues or improvements"""
        
        explanation = await self.llm.generate(prompt)
        return explanation





