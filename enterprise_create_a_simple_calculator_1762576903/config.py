import os
import json
from typing import Dict, Any, Optional

class Config:
    """
    A class to manage configuration settings for the calculator application.
    Configuration is loaded from a JSON file, with support for environment variables.
    """

    def __init__(self, config_file_path: str = "config.json"):
        """
        Initializes the Config object.

        Args:
            config_file_path (str, optional): Path to the configuration JSON file.
                Defaults to "config.json".
        """
        self.config_file_path = config_file_path
        self._config: Dict[str, Any] = {}
        self.load_config()

    def load_config(self) -> None:
        """
        Loads configuration from the specified JSON file.
        Handles file not found and invalid JSON format errors.
        Also supports overriding configuration values with environment variables.
        """
        try:
            with open(self.config_file_path, "r") as f:
                self._config = json.load(f)
        except FileNotFoundError:
            print(f"Warning: Configuration file not found at {self.config_file_path}. Using default settings.")
            self._config = {}  # Initialize with an empty dictionary in case of missing file
        except json.JSONDecodeError as e:
            raise ValueError(f"Error decoding JSON in {self.config_file_path}: {e}") from e
        except Exception as e:
            raise RuntimeError(f"An unexpected error occurred while loading config: {e}") from e

        self._override_with_env_vars()

    def _override_with_env_vars(self) -> None:
        """
        Overrides configuration values with environment variables, if they exist.
        Environment variables should be named using a prefix and the configuration key, e.g., "CALC_LOG_LEVEL".
        This provides a secure and flexible way to manage sensitive or environment-specific settings.
        """
        prefix = "CALC_"  # Prefix for environment variables
        for key, value in self._config.items():
            env_var_name = prefix + key.upper()
            if env_var_name in os.environ:
                # Attempt to convert the environment variable to the original type
                try:
                    original_type = type(value)
                    if original_type is bool:  # Special handling for boolean conversion
                        env_value = os.environ[env_var_name].lower() == "true"
                    else:
                        env_value = original_type(os.environ[env_var_name])
                    self._config[key] = env_value
                except ValueError:
                    print(f"Warning: Could not convert environment variable {env_var_name} to the correct type. Keeping the original value.")
                except Exception as e:
                    print(f"Warning: Error processing environment variable {env_var_name}: {e}. Keeping the original value.")


    def get(self, key: str, default: Optional[Any] = None) -> Any:
        """
        Retrieves a configuration value by key.

        Args:
            key (str): The key of the configuration value to retrieve.
            default (Any, optional): The default value to return if the key is not found.
                Defaults to None.

        Returns:
            Any: The configuration value, or the default value if the key is not found.
        """
        try:
            return self._config[key]
        except KeyError:
            if default is not None:
                return default
            else:
                raise KeyError(f"Configuration key '{key}' not found.")

    def set(self, key: str, value: Any) -> None:
        """
        Sets a configuration value for the given key.

        Args:
            key (str): The key to set.
            value (Any): The value to set for the key.
        """
        if not isinstance(key, str):
            raise TypeError("Key must be a string.")
        self._config[key] = value

    def save_config(self) -> None:
        """
        Saves the current configuration to the JSON file.
        """
        try:
            with open(self.config_file_path, "w") as f:
                json.dump(self._config, f, indent=4)
        except Exception as e:
            raise RuntimeError(f"Error saving configuration to {self.config_file_path}: {e}") from e