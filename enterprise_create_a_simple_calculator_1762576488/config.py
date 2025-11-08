# config.py

import json
from typing import Dict, Any, Optional
import os

class Config:
    """
    A class to manage the calculator configuration.  It loads settings from a JSON file.
    """

    def __init__(self, config_file_path: str = "config.json") -> None:
        """
        Initializes the Config object.

        Args:
            config_file_path: The path to the JSON configuration file. Defaults to 'config.json'.
        """
        self.config_file_path = config_file_path
        self.config_data: Dict[str, Any] = {}
        self.load_config()


    def load_config(self) -> None:
        """
        Loads the configuration from the JSON file specified in config_file_path.
        Handles potential errors during file reading and JSON parsing.
        """
        try:
            # Secure file access: avoid hardcoding file paths and prevent path traversal
            # os.path.abspath ensures the path is absolute and resolves symlinks.
            # This prevents issues if the working directory changes.

            abs_file_path = os.path.abspath(self.config_file_path)
            
            with open(abs_file_path, "r") as f:
                # Load the JSON data into the config_data dictionary.
                # json.load handles the JSON parsing.
                self.config_data = json.load(f)

        except FileNotFoundError:
            # Handle the case where the configuration file does not exist.
            print(f"Error: Configuration file not found at {self.config_file_path}. Using default settings.")
            self.config_data = self.get_default_config() # Load default config if file not found
        except json.JSONDecodeError as e:
            # Handle errors if the JSON file is malformed.
            print(f"Error: Invalid JSON format in {self.config_file_path}: {e}. Using default settings.")
            self.config_data = self.get_default_config()  # Load default config if JSON is invalid
        except Exception as e:
            # Handle other potential errors during file reading.
            print(f"Error: An unexpected error occurred while loading the configuration: {e}. Using default settings.")
            self.config_data = self.get_default_config() # Load default config if any other error occurred


    def get(self, key: str, default: Optional[Any] = None) -> Any:
        """
        Retrieves a configuration value by key.

        Args:
            key: The key of the configuration value to retrieve.
            default: The default value to return if the key is not found.

        Returns:
            The configuration value if the key is found, otherwise the default value.
        """
        return self.config_data.get(key, default)
    
    def get_default_config(self) -> Dict[str, Any]:
        """
        Returns a dictionary containing default configuration settings.
        This provides a fallback in case the configuration file is missing or corrupt.

        Returns:
            A dictionary containing default configuration settings.
        """
        return {
            "precision": 2,
            "max_history_length": 10,
            "theme": "light"
        }

if __name__ == '__main__':
    # Example Usage
    config = Config()

    # Access configuration values
    precision = config.get("precision")
    max_history = config.get("max_history_length")
    theme = config.get("theme", "default_theme")  # Provide a default value for theme if it's missing

    print(f"Precision: {precision}")
    print(f"Max History Length: {max_history}")
    print(f"Theme: {theme}")