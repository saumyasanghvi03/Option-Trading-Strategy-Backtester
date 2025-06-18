"""
This module handles loading and parsing of strategy configuration files.
It currently supports JSON format.
"""
import json
from typing import Dict, Optional # Changed from dict | None for older Python compatibility if needed by subtask env

def load_strategy_config(config_path: str) -> Optional[Dict]:
    """
    Loads a strategy configuration from a JSON file.

    Args:
        config_path: The path to the JSON configuration file.

    Returns:
        A dictionary containing the strategy configuration,
        or None if an error occurs.
    """
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        # Basic validation: Check if it's a dictionary (JSON object)
        if not isinstance(config, dict):
            print(f"Error: Configuration file {config_path} does not contain a valid JSON object.")
            return None
        return config
    except FileNotFoundError:
        print(f"Error: Configuration file {config_path} not found.")
        return None
    except json.JSONDecodeError as e:
        print(f"Error: Could not decode JSON from {config_path}. Details: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred while reading config {config_path}: {e}")
        return None
