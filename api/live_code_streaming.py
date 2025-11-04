"""
SuperAgent v8.0 - Live Code Streaming
Line-by-Line Animation with Real-Time Visualization
WebSocket-based streaming for low-latency delivery
"""

import asyncio
import json
import time
from typing import Dict, List, Any, AsyncGenerator, Callable
from dataclasses import dataclass
from enum import Enum


class StreamEventType(Enum):
    """Types of streaming events"""
    CODE_LINE = "code_line"
    SYNTAX_HIGHLIGHT = "syntax_highlight"
    TYPE_HINT = "type_hint"
    COMMENT = "comment"
    EXECUTION_START = "execution_start"
    EXECUTION_END = "execution_end"
    ERROR = "error"
    PERFORMANCE_METRIC = "performance_metric"
    COMPLETION = "completion"


@dataclass
class StreamEvent:
    """A single streaming event"""
    event_type: StreamEventType
    content: str
    line_number: int
    timestamp: float
    metadata: Dict[str, Any]


class CodeHighlighter:
    """Syntax highlighting for code"""
    
    KEYWORDS = {
        "python": ["def", "class", "if", "else", "for", "while", "return", "import", "from", "async", "await"],
        "javascript": ["function", "const", "let", "var", "if", "else", "for", "while", "return", "import", "export", "async", "await"],
        "typescript": ["function", "const", "let", "var", "if", "else", "for", "while", "return", "import", "export", "async", "await", "interface", "type"],
    }
    
    def highlight_line(self, line: str, language: str = "python") -> Dict[str, Any]:
        """Highlight a single line of code"""
        highlighted = line
        keywords = self.KEYWORDS.get(language, [])
        
        # Identify keywords
        keyword_positions = []
        for keyword in keywords:
            if keyword in line:
                keyword_positions.append({
                    "keyword": keyword,
                    "position": line.find(keyword),
                    "type": "keyword"
                })
        
        # Identify strings
        string_positions = []
        in_string = False
        string_char = None
        for i, char in enumerate(line):
            if char in ['"', "'"]:
                if not in_string:
                    in_string = True
                    string_char = char
                elif char == string_char:
                    in_string = False
                    string_positions.append({"start": i, "type": "string"})
        
        # Identify comments
        comment_start = line.find("#") if language == "python" else line.find("//")
        
        return {
            "original": line,
            "highlighted": highlighted,
            "keywords": keyword_positions,
            "strings": string_positions,
            "comment_start": comment_start if comment_start != -1 else None,
        }


class TypeHintExtractor:
    """Extract and display type hints"""
    
    def extract_type_hints(self, line: str, language: str = "python") -> List[Dict[str, str]]:
        """Extract type hints from a line"""
        hints = []
        
        if language == "python":
            if "->" in line:
                return_type = line.split("->")[1].strip().rstrip(":")
                hints.append({
                    "type": "return_type",
                    "value": return_type,
                    "display": f"→ {return_type}"
                })
            
            if ":" in line and "=" in line:
                parts = line.split(":")
                if len(parts) >= 2:
                    var_type = parts[1].split("=")[0].strip()
                    hints.append({
                        "type": "variable_type",
                        "value": var_type,
                        "display": f": {var_type}"
                    })
        
        elif language in ["typescript", "javascript"]:
            if ":" in line and not line.strip().startswith("//"):
                parts = line.split(":")
                if len(parts) >= 2:
                    var_type = parts[1].split("=")[0].strip()
                    hints.append({
                        "type": "variable_type",
                        "value": var_type,
                        "display": f": {var_type}"
                    })
        
        return hints


class PerformanceMetricsCollector:
    """Collect performance metrics during streaming"""
    
    def __init__(self):
        self.start_time = None
        self.line_times = []
    
    def start(self):
        """Start collecting metrics"""
        self.start_time = time.time()
    
    def record_line(self, line_number: int):
        """Record time for a line"""
        elapsed = time.time() - self.start_time
        self.line_times.append({
            "line": line_number,
            "elapsed": elapsed,
            "rate": line_number / elapsed if elapsed > 0 else 0
        })
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get collected metrics"""
        if not self.line_times:
            return {}
        
        total_time = time.time() - self.start_time
        total_lines = len(self.line_times)
        
        return {
            "total_time": total_time,
            "total_lines": total_lines,
            "average_time_per_line": total_time / total_lines if total_lines > 0 else 0,
            "lines_per_second": total_lines / total_time if total_time > 0 else 0,
        }


class LiveCodeStreamer:
    """Live code streaming with animation and visualization"""
    
    def __init__(self, language: str = "python"):
        self.language = language
        self.highlighter = CodeHighlighter()
        self.type_extractor = TypeHintExtractor()
        self.metrics = PerformanceMetricsCollector()
    
    async def stream_code(self, code: str, callback: Callable[[StreamEvent], None] = None, delay_per_line: float = 0.1) -> AsyncGenerator[StreamEvent, None]:
        """
        Stream code line-by-line with animation
        
        Args:
            code: Code to stream
            callback: Optional callback for each event
            delay_per_line: Delay between lines (seconds)
            
        Yields:
            StreamEvent objects
        """
        
        self.metrics.start()
        lines = code.split("\n")
        
        # Start execution event
        start_event = StreamEvent(
            event_type=StreamEventType.EXECUTION_START,
            content=f"Starting code generation for {len(lines)} lines",
            line_number=0,
            timestamp=time.time(),
            metadata={"language": self.language}
        )
        if callback:
            callback(start_event)
        yield start_event
        
        # Stream each line
        for line_num, line in enumerate(lines, 1):
            # Add delay for animation effect
            await asyncio.sleep(delay_per_line)
            
            # Main code line event
            code_event = StreamEvent(
                event_type=StreamEventType.CODE_LINE,
                content=line,
                line_number=line_num,
                timestamp=time.time(),
                metadata={
                    "indent_level": len(line) - len(line.lstrip()),
                    "is_empty": len(line.strip()) == 0,
                }
            )
            if callback:
                callback(code_event)
            yield code_event
            
            # Syntax highlighting event
            highlighting = self.highlighter.highlight_line(line, self.language)
            highlight_event = StreamEvent(
                event_type=StreamEventType.SYNTAX_HIGHLIGHT,
                content=json.dumps(highlighting),
                line_number=line_num,
                timestamp=time.time(),
                metadata={"language": self.language}
            )
            if callback:
                callback(highlight_event)
            yield highlight_event
            
            # Type hints event
            type_hints = self.type_extractor.extract_type_hints(line, self.language)
            if type_hints:
                for hint in type_hints:
                    type_event = StreamEvent(
                        event_type=StreamEventType.TYPE_HINT,
                        content=hint["display"],
                        line_number=line_num,
                        timestamp=time.time(),
                        metadata=hint
                    )
                    if callback:
                        callback(type_event)
                    yield type_event
            
            # Comment event
            if "#" in line and self.language == "python":
                comment_start = line.find("#")
                comment_text = line[comment_start:]
                comment_event = StreamEvent(
                    event_type=StreamEventType.COMMENT,
                    content=comment_text,
                    line_number=line_num,
                    timestamp=time.time(),
                    metadata={"comment_start": comment_start}
                )
                if callback:
                    callback(comment_event)
                yield comment_event
            
            # Performance metrics event
            self.metrics.record_line(line_num)
            if line_num % 10 == 0:  # Every 10 lines
                metrics = self.metrics.get_metrics()
                metrics_event = StreamEvent(
                    event_type=StreamEventType.PERFORMANCE_METRIC,
                    content=json.dumps(metrics),
                    line_number=line_num,
                    timestamp=time.time(),
                    metadata=metrics
                )
                if callback:
                    callback(metrics_event)
                yield metrics_event
        
        # Completion event
        final_metrics = self.metrics.get_metrics()
        completion_event = StreamEvent(
            event_type=StreamEventType.COMPLETION,
            content=f"Code generation complete: {len(lines)} lines in {final_metrics.get('total_time', 0):.2f}s",
            line_number=len(lines),
            timestamp=time.time(),
            metadata=final_metrics
        )
        if callback:
            callback(completion_event)
        yield completion_event
    
    async def stream_to_websocket(self, code: str, websocket_send: Callable[[str], Any], delay_per_line: float = 0.1):
        """Stream code to WebSocket client"""
        async for event in self.stream_code(code, delay_per_line=delay_per_line):
            message = {
                "event_type": event.event_type.value,
                "content": event.content,
                "line_number": event.line_number,
                "timestamp": event.timestamp,
                "metadata": event.metadata,
            }
            await websocket_send(json.dumps(message))


# API Endpoints
async def stream_code_endpoint(code: str, language: str = "python", delay_per_line: float = 0.1) -> AsyncGenerator[Dict[str, Any], None]:
    """API endpoint for live code streaming"""
    streamer = LiveCodeStreamer(language)
    
    async for event in streamer.stream_code(code, delay_per_line=delay_per_line):
        yield {
            "event_type": event.event_type.value,
            "content": event.content,
            "line_number": event.line_number,
            "timestamp": event.timestamp,
            "metadata": event.metadata,
        }


async def stream_code_with_callback(code: str, language: str = "python", delay_per_line: float = 0.1) -> List[Dict[str, Any]]:
    """Collect all streaming events"""
    streamer = LiveCodeStreamer(language)
    events = []
    
    def collect_event(event: StreamEvent):
        events.append({
            "event_type": event.event_type.value,
            "content": event.content,
            "line_number": event.line_number,
            "timestamp": event.timestamp,
            "metadata": event.metadata,
        })
    
    async for _ in streamer.stream_code(code, callback=collect_event, delay_per_line=delay_per_line):
        pass
    
    return events
