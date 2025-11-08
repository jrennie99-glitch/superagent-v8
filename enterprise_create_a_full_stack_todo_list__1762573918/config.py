import os
from typing import Optional, Union

class Config:
    """
    Base configuration class for the Flask application.
    """
    DEBUG: bool = False
    TESTING: bool = False
    SECRET_KEY: str = os.environ.get("SECRET_KEY", "super_secret_key")  # Use environment variable, default for dev only!
    #  Ideally store in a more secure way (e.g., Vault) in prod

    # Security Headers
    SESSION_COOKIE_SECURE: bool = True  # Only send cookies over HTTPS in production
    REMEMBER_COOKIE_SECURE: bool = True
    SESSION_COOKIE_HTTPONLY: bool = True  # Prevent client-side JavaScript access
    REMEMBER_COOKIE_HTTPONLY: bool = True
    #  Consider Content-Security-Policy header for extra protection

    DATABASE_URI: Optional[str] = None # Abstracted database URI; to be set by subclasses

    @staticmethod
    def init_app(app):
        """
        Initialize the application with the configuration.  Placeholder for customizations.
        """
        pass

class DevelopmentConfig(Config):
    """
    Configuration for development environment.
    """
    DEBUG: bool = True
    TESTING: bool = True
    DATABASE_URI: str = "sqlite:///dev.db"  # Development database
    SESSION_COOKIE_SECURE: bool = False   # Allow cookies over HTTP during development
    REMEMBER_COOKIE_SECURE: bool = False

class TestingConfig(Config):
    """
    Configuration for testing environment.  Uses an in-memory SQLite database.
    """
    TESTING: bool = True
    DATABASE_URI: str = "sqlite:///:memory:"  # In-memory database for tests
    SESSION_COOKIE_SECURE: bool = False
    REMEMBER_COOKIE_SECURE: bool = False
    WTF_CSRF_ENABLED: bool = False    # Disable CSRF protection for testing.  Use with caution


class ProductionConfig(Config):
    """
    Configuration for production environment.
    """
    DATABASE_URI: str = os.environ.get("DATABASE_URL")  # Get database URL from environment
    # Example DATABASE_URL  "postgresql://user:password@host:port/database"

    if not DATABASE_URI:
        raise ValueError("DATABASE_URL environment variable is not set for production.")

    # Additional security considerations:
    # - Implement proper logging and monitoring.
    # - Use a web server like Gunicorn or uWSGI in front of Flask.
    # - Configure the web server with appropriate security settings.


config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig, # Default config if env var not set.  Change for PROD!
}


def get_config(config_name: str) -> Union[Config, DevelopmentConfig, TestingConfig, ProductionConfig]:
    """
    Retrieves the configuration based on the provided name.

    Args:
        config_name: The name of the configuration to retrieve (e.g., 'development', 'production').

    Returns:
        An instance of the corresponding configuration class.
        Returns the default configuration if the specified config_name is not found.
    """
    try:
        return config[config_name]
    except KeyError:
        return config["default"]  # Return the default config if config_name is not valid