"""Configuration management for SuperAgent."""

import os
from pathlib import Path
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class ModelConfig(BaseModel):
    """Model configuration."""
    provider: str = "anthropic"
    name: str = "claude-sonnet-4-5-20250929"  # Latest Claude 4.5 Sonnet (September 2025)
    temperature: float = 0.7
    max_tokens: int = 8000
    top_p: float = 0.95
    
    # Auto-selection settings
    auto_select: bool = True
    prioritize_speed: bool = False
    prioritize_cost: bool = False


class PerformanceConfig(BaseModel):
    """Performance configuration."""
    async_enabled: bool = True
    parallel_tasks: bool = True
    max_workers: int = 8
    cache_ttl: int = 3600
    use_gpu: bool = False


class DebuggingConfig(BaseModel):
    """Debugging configuration."""
    auto_fix_enabled: bool = True
    fix_confidence_threshold: float = 0.9
    max_fix_attempts: int = 3
    trace_depth: int = 10
    visual_debugging: bool = True


class TestingConfig(BaseModel):
    """Testing configuration."""
    auto_generate_tests: bool = True
    coverage_threshold: int = 80
    run_tests_before_deploy: bool = True
    frameworks: Dict[str, str] = Field(default_factory=lambda: {
        "python": "pytest",
        "javascript": "jest",
        "java": "junit"
    })


class DeploymentConfig(BaseModel):
    """Deployment configuration."""
    auto_deploy: bool = False
    platforms: list = Field(default_factory=lambda: ["heroku", "vercel", "aws"])
    git_auto_commit: bool = True


class Config:
    """Main configuration class for SuperAgent."""

    def __init__(self, config_path: Optional[str] = None):
        """Initialize configuration.
        
        Args:
            config_path: Path to YAML configuration file
        """
        self.config_path = config_path or "config.yaml"
        self.config_data = self._load_config()
        
        # API Keys
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY", "")
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "")
        self.groq_api_key = os.getenv("GROQ_API_KEY", "")
        
        # Redis
        self.redis_host = os.getenv("REDIS_HOST", "localhost")
        self.redis_port = int(os.getenv("REDIS_PORT", "6379"))
        self.redis_password = os.getenv("REDIS_PASSWORD", "")
        self.redis_db = int(os.getenv("REDIS_DB", "0"))
        
        # Performance
        self.max_workers = int(os.getenv("MAX_WORKERS", "8"))
        self.cache_enabled = os.getenv("CACHE_ENABLED", "true").lower() == "true"
        
        # Initialize sub-configs
        self.model = ModelConfig(**self.config_data.get("models", {}).get("primary", {}))
        self.performance = PerformanceConfig(**self.config_data.get("performance", {}))
        self.debugging = DebuggingConfig(**self.config_data.get("debugging", {}))
        self.testing = TestingConfig(**self.config_data.get("testing", {}))
        self.deployment = DeploymentConfig(**self.config_data.get("deployment", {}))
        
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML or JSON file."""
        import logging
        logger = logging.getLogger(__name__)
        
        config_file = Path(self.config_path)
        if not config_file.exists():
            logger.info(f"Config file {self.config_path} does not exist, using defaults")
            return {}
        
        # Try YAML first, fallback to JSON
        try:
            import yaml
            with open(config_file, 'r') as f:
                data = yaml.safe_load(f) or {}
                logger.info(f"Loaded config from YAML: {self.config_path}")
                return data
        except ImportError:
            # YAML not available, try JSON
            import json
            with open(config_file, 'r') as f:
                try:
                    data = json.load(f) or {}
                    logger.info(f"Loaded config from JSON: {self.config_path}")
                    return data
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse {self.config_path} as JSON: {e}")
                    return {}
        except Exception as e:
            # YAML parse failed, try JSON
            logger.warning(f"Failed to parse {self.config_path} as YAML: {e}, trying JSON")
            import json
            with open(config_file, 'r') as f:
                try:
                    data = json.load(f) or {}
                    logger.info(f"Loaded config from JSON: {self.config_path}")
                    return data
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse {self.config_path} as JSON: {e}")
                    return {}
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key.
        
        Args:
            key: Configuration key (supports dot notation)
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        keys = key.split('.')
        value = self.config_data
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
            if value is None:
                return default
        return value
    
    def validate(self) -> bool:
        """Validate configuration.
        
        Returns:
            True if configuration is valid
        """
        # Check if at least one LLM API key is set
        if not self.anthropic_api_key and not self.groq_api_key and not self.openai_api_key:
            raise ValueError("No LLM API key set. Set ANTHROPIC_API_KEY, GROQ_API_KEY, or OPENAI_API_KEY")
        return True

