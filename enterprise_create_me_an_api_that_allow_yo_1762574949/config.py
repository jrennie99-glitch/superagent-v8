import os
from typing import Dict, Any

# Define default values for configuration options.  These serve as a fallback
# and also document all expected configuration values.  Sensitive values
# should have a default of None and be required to be set via environment
# variables or other secure configuration management.
DEFAULT_CONFIG: Dict[str, Any] = {
    "API_TITLE": "Social Media Automation API",
    "API_VERSION": "1.0",
    "API_DESCRIPTION": "API for automated posting to social media platforms.",
    "DEBUG_MODE": False,
    "PORT": 8000,
    "HOST": "0.0.0.0",
    "SOCIAL_MEDIA_CREDENTIALS": None,  # Required, must be securely configured.  Example: {'twitter': {'api_key': '...', 'api_secret': '...'}, 'facebook': {'access_token': '...'}}
    "CONTENT_GENERATION_API_URL": None, # Optional, if internal generation is desired.
    "CONTENT_GENERATION_API_KEY": None, # API key for content generation service.  Required if using CONTENT_GENERATION_API_URL
    "DATABASE_URL": "sqlite:///./social_media.db", # Optional, use in memory DB if None
    "LOG_LEVEL": "INFO", # Options: DEBUG, INFO, WARNING, ERROR, CRITICAL
    "LOG_FORMAT": "%(asctime)s - %(name)s - %(levelname)s - %(message)s", # Customizable log format
    "CORS_ORIGINS": ["*"], # List of allowed origins for CORS.  Restrict in production!
    "RATE_LIMIT": "100/minute",  # Format: <requests>/<period>.  Example: 100/minute, 10/hour
    "JWT_SECRET_KEY": None, # Secure secret key for JWT. MUST be changed in production.
    "JWT_ALGORITHM": "HS256", # Algorithm for JWT encoding.
    "JWT_EXPIRY_MINUTES": 30, # JWT expiry time in minutes.
}


def load_config() -> Dict[str, Any]:
    """
    Loads configuration from environment variables, falling back to defaults.

    Raises:
        ValueError: If required configuration values are missing.
    """

    config = DEFAULT_CONFIG.copy()

    # Override defaults with environment variables if they are set
    for key in config:
        env_value = os.getenv(key)
        if env_value is not None:
            # Attempt to convert environment variables to their correct type.
            original_type = type(config[key])
            try:
                if original_type is bool:
                    config[key] = env_value.lower() in ('true', '1', 't')  # Handle boolean values
                elif original_type is int:
                    config[key] = int(env_value)
                elif original_type is list:
                     config[key] = [item.strip() for item in env_value.split(',')] # Handle lists (comma separated)
                else:
                    config[key] = env_value
            except ValueError as e:
                print(f"Warning: Could not convert environment variable {key} with value {env_value} to type {original_type}. Using default value instead. Error: {e}")
                continue # Use default value in this case.

    # Validate required configurations
    if config["SOCIAL_MEDIA_CREDENTIALS"] is None:
        try:
            import json
            credentials_string = os.getenv("SOCIAL_MEDIA_CREDENTIALS_JSON")
            if credentials_string:
                config["SOCIAL_MEDIA_CREDENTIALS"] = json.loads(credentials_string)
            else:
                raise ValueError("SOCIAL_MEDIA_CREDENTIALS or SOCIAL_MEDIA_CREDENTIALS_JSON must be configured.")
        except (json.JSONDecodeError, TypeError) as e:
            raise ValueError(f"Invalid JSON for SOCIAL_MEDIA_CREDENTIALS_JSON: {e}") from e


    if config["JWT_SECRET_KEY"] is None:
        secret = os.getenv("JWT_SECRET_KEY")
        if secret:
            config["JWT_SECRET_KEY"] = secret
        else:
            raise ValueError("JWT_SECRET_KEY must be configured for authentication.")


    return config


# Load configuration immediately upon import.
CONFIG = load_config()


def get_config() -> Dict[str, Any]:
    """
    Returns the loaded configuration.  This is the main access point for
    configuration data.
    """
    return CONFIG