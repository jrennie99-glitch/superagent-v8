import json
import os
from typing import Dict, Any


class ConfigError(Exception):
    """Custom exception for configuration errors."""
    pass


class Config:
    """
    Configuration class for the calculator app.
    Loads configuration from a JSON file and provides access to configuration values.
    """

    def __init__(self, config_file_path: str = "config.json") -> None:
        """
        Initializes the Config object.

        Args:
            config_file_path: The path to the configuration file (JSON). Defaults to 'config.json'.
        """
        self._config: Dict[str, Any] = {}  # Initialize with an empty dictionary
        self._config_file_path: str = config_file_path
        self.load_config()

    def load_config(self) -> None:
        """
        Loads configuration from the specified JSON file.

        Raises:
            ConfigError: If the configuration file is missing, invalid JSON, or contains unexpected values.
        """
        try:
            # Secure file opening: prevent path traversal vulnerabilities
            abs_file_path = os.path.abspath(self._config_file_path)
            if not os.path.isfile(abs_file_path):
                raise FileNotFoundError(f"Configuration file not found: {abs_file_path}")

            with open(abs_file_path, "r") as f:
                try:
                    self._config = json.load(f)
                except json.JSONDecodeError as e:
                    raise ConfigError(f"Invalid JSON format in configuration file: {e}")

        except FileNotFoundError as e:
            raise ConfigError(f"Configuration file error: {e}")
        except ConfigError as e:
            raise e  # Re-raise custom ConfigError
        except Exception as e:
            raise ConfigError(f"An unexpected error occurred while loading the configuration: {e}")

        self.validate_config()  # Validate after loading.

    def validate_config(self) -> None:
        """
        Validates the loaded configuration. Override this method in subclasses to 
        add custom validation logic.

        Raises:
            ConfigError: If any validation rules are violated.
        """
        # Example validation - can be extended with more checks.
        #  Currently, performs minimal validation - ensures config isn't empty.
        if not self._config:
            raise ConfigError("Configuration is empty after loading.")

    def get(self, key: str) -> Any:
        """
        Retrieves a configuration value by key.

        Args:
            key: The key of the configuration value to retrieve.

        Returns:
            The configuration value associated with the specified key.

        Raises:
            ConfigError: If the specified key is not found in the configuration.
        """
        try:
            return self._config[key]
        except KeyError:
            raise ConfigError(f"Configuration key not found: {key}")
        except Exception as e:
            raise ConfigError(f"An unexpected error occurred while getting the configuration: {e}")


# Example usage (for demonstration and testing purposes)
if __name__ == "__main__":
    # Create a dummy config.json file for testing
    example_config = {
        "app_name": "My Calculator",
        "version": "1.0",
        "theme": "light",
        "log_level": "INFO"
    }

    try:
        with open("config.json", "w") as f:
            json.dump(example_config, f, indent=4)  # Pretty-print the JSON
    except Exception as e:
        print(f"Error creating example config file: {e}")

    try:
        config = Config()
        app_name = config.get("app_name")
        version = config.get("version")
        print(f"App Name: {app_name}, Version: {version}")

        # Example of a key that doesn't exist
        # theme = config.get("invalid_key")  # This will raise a ConfigError
    except ConfigError as e:
        print(f"Configuration Error: {e}")
    except Exception as e:
        print(f"Unexpected Error: {e}")

    # Clean up the dummy config.json file after testing
    try:
        os.remove("config.json")
    except FileNotFoundError:
        pass  # It's okay if the file doesn't exist (e.g., if creating it failed)
    except Exception as e:
        print(f"Error removing config file: {e}")