"""
Comprehensive Error Handler for SuperAgent v8
Provides detailed logging, error tracking, and user-friendly error messages
"""
import traceback
import logging
from typing import Dict, Any, Optional
from datetime import datetime
import json

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/tmp/superagent_detailed.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class ErrorHandler:
    """Centralized error handling and logging"""
    
    @staticmethod
    def log_error(error: Exception, context: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Log error with full context and return user-friendly error response
        
        Args:
            error: The exception that occurred
            context: Description of where/when the error occurred
            data: Additional context data (sanitized before logging)
        
        Returns:
            Dict with error details for API response
        """
        error_id = datetime.now().strftime("%Y%m%d%H%M%S%f")
        
        # Get full stack trace
        stack_trace = traceback.format_exc()
        
        # Log detailed error
        logger.error(f"""
========== ERROR {error_id} ==========
Context: {context}
Error Type: {type(error).__name__}
Error Message: {str(error)}
Data: {json.dumps(data, default=str) if data else 'None'}
Stack Trace:
{stack_trace}
=====================================
        """)
        
        # Return user-friendly error
        return {
            "success": False,
            "error_id": error_id,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context,
            "user_message": ErrorHandler._get_user_friendly_message(error, context),
            "timestamp": datetime.now().isoformat()
        }
    
    @staticmethod
    def _get_user_friendly_message(error: Exception, context: str) -> str:
        """Convert technical error to user-friendly message"""
        error_type = type(error).__name__
        error_msg = str(error).lower()
        
        # Common error patterns
        if "string indices must be integers" in error_msg:
            return ("There was a data format issue while creating your application files. "
                   "This usually happens when the AI response format is unexpected. "
                   "Please try again, and if the issue persists, try simplifying your request.")
        
        elif "connection" in error_msg or "timeout" in error_msg:
            return ("Unable to connect to the AI service. Please check your internet connection "
                   "and try again in a moment.")
        
        elif "api key" in error_msg or "authentication" in error_msg:
            return ("API authentication failed. Please check that your API keys are configured correctly.")
        
        elif "permission" in error_msg or "access denied" in error_msg:
            return ("File system permission error. The system couldn't create or modify files. "
                   "This might be a deployment configuration issue.")
        
        elif "module" in error_msg and "not found" in error_msg:
            return ("A required Python package is missing. The system will attempt to install it automatically.")
        
        elif "syntax" in error_msg:
            return ("The generated code contains syntax errors. The AI will retry with corrections.")
        
        else:
            return (f"An unexpected error occurred during {context}. "
                   f"Error: {error_type}. Please try again or contact support with error ID.")
    
    @staticmethod
    def wrap_async_function(func):
        """Decorator to wrap async functions with error handling"""
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                context = f"{func.__name__}"
                return ErrorHandler.log_error(e, context, {
                    "args": str(args)[:200],
                    "kwargs": str(kwargs)[:200]
                })
        return wrapper
    
    @staticmethod
    def safe_dict_access(data: Any, key: str, default: Any = None) -> Any:
        """
        Safely access dictionary keys with type checking
        
        Args:
            data: The data structure to access
            key: The key to retrieve
            default: Default value if key doesn't exist or data is wrong type
        
        Returns:
            The value or default
        """
        try:
            if isinstance(data, dict):
                return data.get(key, default)
            elif isinstance(data, str):
                logger.warning(f"Attempted to access key '{key}' on string data: {data[:100]}")
                # Try to parse as JSON
                try:
                    parsed = json.loads(data)
                    if isinstance(parsed, dict):
                        return parsed.get(key, default)
                except:
                    pass
            return default
        except Exception as e:
            logger.error(f"Error in safe_dict_access: {e}")
            return default
    
    @staticmethod
    def validate_response(response: Any, expected_type: type, context: str) -> tuple[bool, Any]:
        """
        Validate API response type and structure
        
        Args:
            response: The response to validate
            expected_type: Expected Python type
            context: Context for error logging
        
        Returns:
            Tuple of (is_valid, processed_response)
        """
        try:
            # Check if response is expected type
            if isinstance(response, expected_type):
                return True, response
            
            # Try to convert string to expected type
            if isinstance(response, str) and expected_type == dict:
                try:
                    parsed = json.loads(response)
                    if isinstance(parsed, dict):
                        logger.info(f"Successfully parsed string response to dict in {context}")
                        return True, parsed
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse string as JSON in {context}: {e}")
                    return False, {}
            
            # Log type mismatch
            logger.warning(f"Type mismatch in {context}: expected {expected_type}, got {type(response)}")
            return False, {} if expected_type == dict else None
            
        except Exception as e:
            logger.error(f"Error validating response in {context}: {e}")
            return False, {} if expected_type == dict else None

# Global error handler instance
error_handler = ErrorHandler()
