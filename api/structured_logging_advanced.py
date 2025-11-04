"""
SuperAgent v8.0 - Advanced Structured Logging
Production-Grade JSON Logging with Console Output and Analytics
"""

import json
import logging
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum


class LogLevel(Enum):
    """Log levels"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@dataclass
class LogEntry:
    """A structured log entry"""
    timestamp: str
    level: str
    message: str
    context: Dict[str, Any]
    metadata: Dict[str, Any]
    duration_ms: Optional[float]
    error: Optional[Dict[str, Any]]
    tags: List[str]


class AdvancedStructuredLogger:
    """Production-grade structured logging system"""
    
    def __init__(self, service_name: str = "superagent", environment: str = "production"):
        self.service_name = service_name
        self.environment = environment
        self.logs: List[LogEntry] = []
        self.start_time = time.time()
    
    def log(self, level: LogLevel, message: str, context: Optional[Dict] = None, 
            metadata: Optional[Dict] = None, duration_ms: Optional[float] = None,
            error: Optional[Exception] = None, tags: Optional[List[str]] = None) -> LogEntry:
        """Log a structured message"""
        
        entry = LogEntry(
            timestamp=datetime.utcnow().isoformat() + "Z",
            level=level.value,
            message=message,
            context=context or {},
            metadata=metadata or {},
            duration_ms=duration_ms,
            error=self._serialize_error(error) if error else None,
            tags=tags or [],
        )
        
        self.logs.append(entry)
        self._print_to_console(entry)
        
        return entry
    
    def debug(self, message: str, **kwargs) -> LogEntry:
        """Log debug message"""
        return self.log(LogLevel.DEBUG, message, **kwargs)
    
    def info(self, message: str, **kwargs) -> LogEntry:
        """Log info message"""
        return self.log(LogLevel.INFO, message, **kwargs)
    
    def warning(self, message: str, **kwargs) -> LogEntry:
        """Log warning message"""
        return self.log(LogLevel.WARNING, message, **kwargs)
    
    def error(self, message: str, **kwargs) -> LogEntry:
        """Log error message"""
        return self.log(LogLevel.ERROR, message, **kwargs)
    
    def critical(self, message: str, **kwargs) -> LogEntry:
        """Log critical message"""
        return self.log(LogLevel.CRITICAL, message, **kwargs)
    
    def _serialize_error(self, error: Exception) -> Dict[str, Any]:
        """Serialize exception for logging"""
        import traceback
        return {
            "type": type(error).__name__,
            "message": str(error),
            "traceback": traceback.format_exc(),
        }
    
    def _print_to_console(self, entry: LogEntry):
        """Print log entry to console"""
        level_color = self._get_level_color(entry.level)
        timestamp = entry.timestamp
        
        console_output = f"[{timestamp}] {level_color}{entry.level}\033[0m: {entry.message}"
        
        if entry.metadata:
            console_output += f" | metadata={json.dumps(entry.metadata)}"
        
        if entry.duration_ms:
            console_output += f" | duration={entry.duration_ms}ms"
        
        if entry.error:
            console_output += f" | error={entry.error['type']}: {entry.error['message']}"
        
        print(console_output)
    
    def _get_level_color(self, level: str) -> str:
        """Get ANSI color for log level"""
        colors = {
            "DEBUG": "\033[36m",
            "INFO": "\033[32m",
            "WARNING": "\033[33m",
            "ERROR": "\033[31m",
            "CRITICAL": "\033[35m",
        }
        return colors.get(level, "")
    
    def get_logs(self, level: Optional[LogLevel] = None, tag: Optional[str] = None, 
                 limit: int = 100) -> List[LogEntry]:
        """Get logs with optional filtering"""
        logs = self.logs
        
        if level:
            logs = [l for l in logs if l.level == level.value]
        
        if tag:
            logs = [l for l in logs if tag in l.tags]
        
        return logs[-limit:]
    
    def export_all_logs(self) -> str:
        """Export all logs as JSON Lines"""
        json_lines = []
        for entry in self.logs:
            json_entry = {
                "timestamp": entry.timestamp,
                "service": self.service_name,
                "environment": self.environment,
                "level": entry.level,
                "message": entry.message,
                "context": entry.context,
                "metadata": entry.metadata,
                "duration_ms": entry.duration_ms,
                "error": entry.error,
                "tags": entry.tags,
            }
            json_lines.append(json.dumps(json_entry))
        
        return "\n".join(json_lines)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get logging statistics"""
        level_counts = {}
        tag_counts = {}
        total_duration = 0
        error_count = 0
        
        for entry in self.logs:
            level_counts[entry.level] = level_counts.get(entry.level, 0) + 1
            
            for tag in entry.tags:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
            
            if entry.duration_ms:
                total_duration += entry.duration_ms
            
            if entry.error:
                error_count += 1
        
        return {
            "total_logs": len(self.logs),
            "by_level": level_counts,
            "by_tag": tag_counts,
            "total_duration_ms": total_duration,
            "average_duration_ms": total_duration / len(self.logs) if self.logs else 0,
            "error_count": error_count,
            "uptime_seconds": time.time() - self.start_time,
        }


# Global logger instance
_global_logger = AdvancedStructuredLogger()


def get_logger() -> AdvancedStructuredLogger:
    """Get global logger instance"""
    return _global_logger


# API Endpoints
async def get_logs_endpoint(level: Optional[str] = None, tag: Optional[str] = None, limit: int = 100) -> Dict[str, Any]:
    """API endpoint to get logs"""
    logger = get_logger()
    
    log_level = LogLevel[level.upper()] if level else None
    logs = logger.get_logs(level=log_level, tag=tag, limit=limit)
    
    return {
        "logs": [
            {
                "timestamp": l.timestamp,
                "level": l.level,
                "message": l.message,
                "context": l.context,
                "metadata": l.metadata,
                "tags": l.tags,
            }
            for l in logs
        ],
        "count": len(logs),
    }


async def export_logs_endpoint() -> str:
    """API endpoint to export all logs as JSON Lines"""
    logger = get_logger()
    return logger.export_all_logs()


async def log_statistics_endpoint() -> Dict[str, Any]:
    """API endpoint for logging statistics"""
    logger = get_logger()
    return logger.get_statistics()
