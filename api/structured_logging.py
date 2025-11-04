"""
Structured Logging
Production-grade logging system
"""
import logging
import json
from datetime import datetime
from typing import Dict, Any
from pathlib import Path

class StructuredLogger:
    """Production-grade structured logging"""
    
    def __init__(self, name: str = "SuperAgent"):
        self.name = name
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # Create logs directory
        Path("logs").mkdir(exist_ok=True)
        
        # File handler with JSON formatting
        file_handler = logging.FileHandler("logs/superagent.log")
        file_handler.setFormatter(JsonFormatter())
        self.logger.addHandler(file_handler)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(ColorFormatter())
        self.logger.addHandler(console_handler)
    
    def log(self, level: str, message: str, **kwargs):
        """Log structured message"""
        extra = {
            "timestamp": datetime.utcnow().isoformat(),
            "logger": self.name,
            **kwargs
        }
        
        if level == "debug":
            self.logger.debug(message, extra=extra)
        elif level == "info":
            self.logger.info(message, extra=extra)
        elif level == "warning":
            self.logger.warning(message, extra=extra)
        elif level == "error":
            self.logger.error(message, extra=extra)
        elif level == "critical":
            self.logger.critical(message, extra=extra)
    
    def info(self, message: str, **kwargs):
        """Log info message"""
        self.log("info", message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error message"""
        self.log("error", message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message"""
        self.log("warning", message, **kwargs)
    
    def debug(self, message: str, **kwargs):
        """Log debug message"""
        self.log("debug", message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        """Log critical message"""
        self.log("critical", message, **kwargs)

class JsonFormatter(logging.Formatter):
    """JSON formatter for structured logs"""
    
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        
        # Add extra fields
        if hasattr(record, "timestamp"):
            log_data["timestamp"] = record.timestamp
        if hasattr(record, "logger"):
            log_data["logger"] = record.logger
        
        # Add any additional attributes
        for key, value in record.__dict__.items():
            if key not in ["name", "msg", "args", "created", "filename", "funcName",
                          "levelname", "levelno", "lineno", "module", "msecs",
                          "message", "pathname", "process", "processName",
                          "relativeCreated", "thread", "threadName", "exc_info",
                          "exc_text", "stack_info", "timestamp", "logger"]:
                log_data[key] = value
        
        return json.dumps(log_data)

class ColorFormatter(logging.Formatter):
    """Colored formatter for console output"""
    
    COLORS = {
        "DEBUG": "\033[36m",     # Cyan
        "INFO": "\033[32m",      # Green
        "WARNING": "\033[33m",   # Yellow
        "ERROR": "\033[31m",     # Red
        "CRITICAL": "\033[35m",  # Magenta
        "RESET": "\033[0m"       # Reset
    }
    
    def format(self, record: logging.LogRecord) -> str:
        color = self.COLORS.get(record.levelname, self.COLORS["RESET"])
        reset = self.COLORS["RESET"]
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return f"{color}[{timestamp}] {record.levelname:8s}{reset} {record.getMessage()}"

# Global logger instance
logger = StructuredLogger()
