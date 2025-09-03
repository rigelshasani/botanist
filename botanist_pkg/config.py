"""
Configuration management for Botanist.
"""

import json
import os

# Default configuration
DEFAULT_CONFIG = {
    "time_thresholds": {
        "seedling_minutes": 25,
        "bud_minutes": 45, 
        "bloom_minutes": 60,
        "queen_minutes": 120
    },
    "min_session_seconds": 30,
    "default_break_minutes": 5
}

CONFIG_FILE = ".botanist_config.json"


def load_config():
    """Load configuration from file or return defaults"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                user_config = json.load(f)
                # Merge with defaults to ensure all keys exist
                config = DEFAULT_CONFIG.copy()
                config.update(user_config)
                return config
        except (json.JSONDecodeError, IOError):
            print(f"Warning: Could not load {CONFIG_FILE}, using defaults")
    
    return DEFAULT_CONFIG.copy()


def save_config(config):
    """Save configuration to file"""
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=2)
        return True
    except IOError as e:
        print(f"Error saving configuration: {e}")
        return False


def get_time_thresholds():
    """Get time thresholds for flower assignment"""
    config = load_config()
    thresholds = config["time_thresholds"]
    return {
        "seedling": thresholds["seedling_minutes"] * 60,  # Convert to seconds
        "bud": thresholds["bud_minutes"] * 60,
        "bloom": thresholds["bloom_minutes"] * 60, 
        "queen": thresholds["queen_minutes"] * 60
    }


def get_min_session_seconds():
    """Get minimum session duration in seconds"""
    config = load_config()
    return config["min_session_seconds"]


def update_time_thresholds(seedling_min=None, bud_min=None, bloom_min=None, queen_min=None):
    """Update time thresholds and save configuration"""
    config = load_config()
    
    if seedling_min is not None:
        config["time_thresholds"]["seedling_minutes"] = seedling_min
    if bud_min is not None:
        config["time_thresholds"]["bud_minutes"] = bud_min
    if bloom_min is not None:
        config["time_thresholds"]["bloom_minutes"] = bloom_min
    if queen_min is not None:
        config["time_thresholds"]["queen_minutes"] = queen_min
    
    return save_config(config)