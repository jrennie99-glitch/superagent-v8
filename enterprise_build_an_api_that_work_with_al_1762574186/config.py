import os
from typing import Optional, Dict, Any
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class Config:
    """
    A class to manage configuration settings for the social media API.
    Loads configuration from a JSON file and provides access to settings.
    """

    def __init__(self, config_file_path: str = "config.json") -> None:
        """
        Initializes the Config object.

        Args:
            config_file_path: The path to the JSON configuration file. Defaults to "config.json".
        """
        self.config_file_path = config_file_path
        self.config_data: Dict[str, Any] = {}
        self.load_config()

    def load_config(self) -> None:
        """
        Loads configuration data from the specified JSON file.
        Handles file not found and JSON decoding errors gracefully.
        """
        try:
            with open(self.config_file_path, "r") as f:
                self.config_data = json.load(f)
            logging.info(f"Configuration loaded successfully from {self.config_file_path}")
        except FileNotFoundError:
            logging.error(f"Configuration file not found at {self.config_file_path}")
            # Raise the exception for handling in the calling code or provide default configuration.
            raise
        except json.JSONDecodeError as e:
            logging.error(f"Error decoding JSON from {self.config_file_path}: {e}")
            # Consider raising a custom exception to indicate a configuration error.
            raise
        except Exception as e:
            logging.error(f"An unexpected error occurred while loading configuration: {e}")
            raise

    def get(self, key: str, default: Optional[Any] = None) -> Any:
        """
        Retrieves a configuration value based on the provided key.

        Args:
            key: The key to retrieve the value for.
            default: The default value to return if the key is not found.  Defaults to None.

        Returns:
            The configuration value associated with the key, or the default value if the key is not found.
        """
        try:
            value = self.config_data.get(key, default)
            if value is None and default is None:
                logging.warning(f"Configuration key '{key}' not found and no default provided.")
            return value
        except Exception as e:
            logging.error(f"Error retrieving configuration value for key '{key}': {e}")
            return default

    def get_str(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """
        Retrieves a configuration value as a string.

        Args:
            key: The key to retrieve the value for.
            default: The default string value to return if the key is not found. Defaults to None.

        Returns:
            The configuration value associated with the key, cast as a string, or the default value if the key is not found.
        """
        value = self.get(key, default)
        if value is None:
            return None
        try:
            return str(value)
        except Exception as e:
            logging.error(f"Error casting configuration value for key '{key}' to string: {e}")
            return default

    def get_int(self, key: str, default: Optional[int] = None) -> Optional[int]:
        """
        Retrieves a configuration value as an integer.

        Args:
            key: The key to retrieve the value for.
            default: The default integer value to return if the key is not found. Defaults to None.

        Returns:
            The configuration value associated with the key, cast as an integer, or the default value if the key is not found.
        """
        value = self.get(key, default)
        if value is None:
            return None
        try:
            return int(value)
        except (ValueError, TypeError) as e:
            logging.error(f"Error casting configuration value for key '{key}' to integer: {e}")
            return default

    def get_bool(self, key: str, default: Optional[bool] = None) -> Optional[bool]:
        """
        Retrieves a configuration value as a boolean.  Handles common boolean string representations.

        Args:
            key: The key to retrieve the value for.
            default: The default boolean value to return if the key is not found. Defaults to None.

        Returns:
            The configuration value associated with the key, cast as a boolean, or the default value if the key is not found.
        """
        value = self.get(key, default)
        if value is None:
            return None

        if isinstance(value, bool):
            return value

        if isinstance(value, str):
            value = value.lower()
            if value in ("true", "1", "yes"):
                return True
            elif value in ("false", "0", "no"):
                return False
            else:
                logging.error(f"Invalid boolean string value for key '{key}': {value}")
                return default  # or raise an exception

        try:
            return bool(value)
        except (ValueError, TypeError) as e:
            logging.error(f"Error casting configuration value for key '{key}' to boolean: {e}")
            return default

    def get_dict(self, key: str, default: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """
        Retrieves a configuration value as a dictionary.

        Args:
            key: The key to retrieve the value for.
            default: The default dictionary value to return if the key is not found. Defaults to None.

        Returns:
            The configuration value associated with the key, cast as a dictionary, or the default value if the key is not found.
        """
        value = self.get(key, default)
        if value is None:
            return None
        if isinstance(value, dict):
            return value
        else:
            logging.error(f"Configuration value for key '{key}' is not a dictionary.")
            return default

    def update_config(self, new_config: Dict[str, Any]) -> None:
        """
        Updates the configuration data with new values.  This does NOT persist the changes to disk.

        Args:
            new_config: A dictionary containing the new configuration values to update.
        """
        try:
            self.config_data.update(new_config)
            logging.info("Configuration updated successfully in memory.")
        except Exception as e:
            logging.error(f"Error updating configuration: {e}")

    def save_config(self) -> None:
        """
        Saves the current configuration data back to the JSON file.
        Important: Ensure proper permissions are set on the config file.
        """
        try:
            # Ensure the config directory exists
            config_dir = os.path.dirname(self.config_file_path)
            if config_dir and not os.path.exists(config_dir):
                os.makedirs(config_dir, exist_ok=True)
                logging.info(f"Created config directory: {config_dir}")

            with open(self.config_file_path, "w") as f:
                json.dump(self.config_data, f, indent=4)  # Use indent for readability
            logging.info(f"Configuration saved successfully to {self.config_file_path}")
        except OSError as e:
            logging.error(f"Error saving configuration to file: {e}")
        except Exception as e:
            logging.error(f"An unexpected error occurred while saving configuration: {e}")


# Example usage (moved to separate main block)
if __name__ == "__main__":
    try:
        # Create a Config object, loading from "config.json"
        config = Config("config.json")

        # Access a string configuration value
        api_key = config.get_str("api_key")
        print(f"API Key: {api_key}")

        # Access an integer configuration value with a default
        port = config.get_int("port", 8080)
        print(f"Port: {port}")

        # Access a boolean configuration value
        debug_mode = config.get_bool("debug_mode", False)
        print(f"Debug Mode: {debug_mode}")

        #Access a dict
        social_media = config.get_dict("social_media")
        print(f"Social Media Config: {social_media}")


        # Update the configuration (in memory)
        config.update_config({"debug_mode": True, "new_setting": "updated_value"})

        # Save the updated configuration to the file
        config.save_config()

    except FileNotFoundError:
        print("Error: Configuration file not found.  Please ensure 'config.json' exists.")
    except json.JSONDecodeError:
        print("Error:  Invalid JSON format in 'config.json'.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")