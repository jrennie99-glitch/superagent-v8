"""Performance profiling and optimization suggestions."""

import cProfile
import pstats
import io
from pathlib import Path
from typing import Dict, Any, List, Optional
import time
import asyncio
import structlog

logger = structlog.get_logger()


class PerformanceProfiler:
    """
    Performance profiler with optimization suggestions.
    
    Features:
    - Runtime profiling
    - Memory profiling
    - Bottleneck detection
    - AI-powered optimization suggestions
    - Performance regression detection
    """
    
    def __init__(self, llm_provider):
        """Initialize profiler.
        
        Args:
            llm_provider: LLM provider
        """
        self.llm = llm_provider
        self.profiles: Dict[str, Any] = {}
    
    async def profile_function(self, func: callable, *args, **kwargs) -> Dict[str, Any]:
        """Profile a function execution.
        
        Args:
            func: Function to profile
            *args, **kwargs: Function arguments
            
        Returns:
            Profile results
        """
        # CPU profiling
        profiler = cProfile.Profile()
        profiler.enable()
        
        start_time = time.time()
        
        # Execute function
        if asyncio.iscoroutinefunction(func):
            result = await func(*args, **kwargs)
        else:
            result = func(*args, **kwargs)
        
        execution_time = time.time() - start_time
        
        profiler.disable()
        
        # Analyze profile
        stats = self._analyze_profile(profiler)
        
        return {
            "function": func.__name__,
            "execution_time": execution_time,
            "stats": stats,
            "result": result
        }
    
    async def profile_file(self, file_path: Path) -> Dict[str, Any]:
        """Profile a Python file.
        
        Args:
            file_path: Path to file
            
        Returns:
            Profile results
        """
        logger.info(f"Profiling file: {file_path}")
        
        # Run file with profiling
        profiler = cProfile.Profile()
        
        try:
            with open(file_path) as f:
                code = compile(f.read(), file_path, 'exec')
                profiler.runcall(exec, code)
            
            # Analyze results
            stats = self._analyze_profile(profiler)
            
            # Get AI suggestions
            suggestions = await self._get_optimization_suggestions(stats, file_path)
            
            return {
                "file": str(file_path),
                "stats": stats,
                "bottlenecks": self._identify_bottlenecks(stats),
                "suggestions": suggestions
            }
        
        except Exception as e:
            logger.error(f"Profiling failed: {e}")
            return {"error": str(e)}
    
    def _analyze_profile(self, profiler: cProfile.Profile) -> Dict[str, Any]:
        """Analyze profile data.
        
        Args:
            profiler: Profile object
            
        Returns:
            Analysis results
        """
        s = io.StringIO()
        ps = pstats.Stats(profiler, stream=s)
        ps.sort_stats('cumulative')
        ps.print_stats(20)  # Top 20 functions
        
        output = s.getvalue()
        
        # Parse stats
        functions = []
        for line in output.split('\n')[5:25]:  # Skip headers
            parts = line.split()
            if len(parts) >= 6:
                functions.append({
                    "ncalls": parts[0],
                    "tottime": float(parts[1]) if parts[1].replace('.', '').isdigit() else 0,
                    "cumtime": float(parts[3]) if len(parts) > 3 and parts[3].replace('.', '').isdigit() else 0,
                    "function": parts[-1] if parts else ""
                })
        
        return {
            "top_functions": functions,
            "raw_output": output
        }
    
    def _identify_bottlenecks(self, stats: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify performance bottlenecks.
        
        Args:
            stats: Profile stats
            
        Returns:
            List of bottlenecks
        """
        bottlenecks = []
        
        functions = stats.get("top_functions", [])
        
        for func in functions[:5]:  # Top 5
            cumtime = func.get("cumtime", 0)
            if cumtime > 0.1:  # More than 100ms
                bottlenecks.append({
                    "function": func["function"],
                    "time": cumtime,
                    "severity": "high" if cumtime > 1.0 else "medium"
                })
        
        return bottlenecks
    
    async def _get_optimization_suggestions(self, stats: Dict[str, Any], 
                                           file_path: Path) -> List[Dict[str, Any]]:
        """Get AI-powered optimization suggestions.
        
        Args:
            stats: Profile stats
            file_path: File path
            
        Returns:
            Optimization suggestions
        """
        bottlenecks = self._identify_bottlenecks(stats)
        
        if not bottlenecks:
            return []
        
        # Read source code for context
        try:
            code = file_path.read_text()
        except:
            code = ""
        
        prompt = f"""Analyze these performance bottlenecks and suggest optimizations:

Bottlenecks:
{bottlenecks}

Code context:
{code[:1500]}

Provide specific optimization suggestions:
1. Caching strategies
2. Algorithm improvements
3. Async/await opportunities
4. Data structure optimizations
5. Parallelization possibilities

Format as JSON: [{{"issue": "...", "suggestion": "...", "impact": "high/medium/low"}}]"""
        
        try:
            result = await self.llm.generate_structured(
                prompt,
                schema={"suggestions": [{"issue": "string", "suggestion": "string", "impact": "string"}]}
            )
            return result.get("suggestions", [])
        except:
            return []
    
    async def memory_profile(self, func: callable, *args, **kwargs) -> Dict[str, Any]:
        """Profile memory usage.
        
        Args:
            func: Function to profile
            *args, **kwargs: Arguments
            
        Returns:
            Memory profile
        """
        try:
            import tracemalloc
            
            tracemalloc.start()
            
            # Execute function
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
            
            current, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            
            return {
                "function": func.__name__,
                "current_memory_mb": current / 1024 / 1024,
                "peak_memory_mb": peak / 1024 / 1024,
                "result": result
            }
        
        except ImportError:
            logger.warning("tracemalloc not available")
            return {"error": "tracemalloc not available"}
    
    async def benchmark_code(self, code: str, iterations: int = 100) -> Dict[str, Any]:
        """Benchmark code snippet.
        
        Args:
            code: Code to benchmark
            iterations: Number of iterations
            
        Returns:
            Benchmark results
        """
        times = []
        
        for _ in range(iterations):
            start = time.time()
            try:
                exec(code)
            except:
                pass
            times.append(time.time() - start)
        
        times.sort()
        
        return {
            "iterations": iterations,
            "min_time": times[0],
            "max_time": times[-1],
            "median_time": times[len(times) // 2],
            "avg_time": sum(times) / len(times)
        }
    
    def compare_performance(self, profile1: Dict[str, Any], 
                           profile2: Dict[str, Any]) -> Dict[str, Any]:
        """Compare two performance profiles.
        
        Args:
            profile1: First profile
            profile2: Second profile
            
        Returns:
            Comparison results
        """
        time1 = profile1.get("execution_time", 0)
        time2 = profile2.get("execution_time", 0)
        
        if time1 == 0:
            speedup = 0
        else:
            speedup = time1 / time2
        
        return {
            "speedup": speedup,
            "faster": "profile2" if speedup > 1 else "profile1",
            "time_diff": abs(time1 - time2),
            "percent_change": ((time2 - time1) / time1 * 100) if time1 != 0 else 0
        }





