"""
Configuration management for Botanist.
"""

import json
import os
import copy
from .paths import config_file_for_read, config_file_for_write
from .utils import validate_time_input

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

def _config_file_for_read() -> str:
    return str(config_file_for_read())

def _config_file_for_write() -> str:
    return str(config_file_for_write())


def _coerce_minutes(value, default_minutes):
    """Coerce a possibly-invalid minute value into a sane integer within 1..1440."""
    try:
        # try direct int first
        iv = int(value)
        if 1 <= iv <= 1440:
            return iv
    except Exception:
        pass
    # fall back to validator that accepts strings
    ok, val = validate_time_input(str(value))
    if ok and val is not None:
        return val
    return default_minutes


def load_config():
    """Load configuration from file, deep-merge defaults, and validate values."""
    base = copy.deepcopy(DEFAULT_CONFIG)

    if os.path.exists(_config_file_for_read()):
        try:
            with open(_config_file_for_read(), "r", encoding="utf-8") as f:
                user_config = json.load(f)
        except (json.JSONDecodeError, IOError):
            print("Warning: Could not load config file, using defaults")
            return base

        # Deep-merge time_thresholds
        user_tt = {}
        if isinstance(user_config, dict):
            user_tt = user_config.get("time_thresholds", {}) or {}

            # Merge known top-level keys
            for k in ("min_session_seconds", "default_break_minutes"):
                if k in user_config:
                    base[k] = user_config[k]

        merged_tt = base["time_thresholds"].copy()
        if isinstance(user_tt, dict):
            merged_tt.update({k: v for k, v in user_tt.items() if k in merged_tt})

        # Validate/coerce minute thresholds
        sm = _coerce_minutes(merged_tt.get("seedling_minutes"), DEFAULT_CONFIG["time_thresholds"]["seedling_minutes"])
        bm = _coerce_minutes(merged_tt.get("bud_minutes"), DEFAULT_CONFIG["time_thresholds"]["bud_minutes"])
        blm = _coerce_minutes(merged_tt.get("bloom_minutes"), DEFAULT_CONFIG["time_thresholds"]["bloom_minutes"])
        qm = _coerce_minutes(merged_tt.get("queen_minutes"), DEFAULT_CONFIG["time_thresholds"]["queen_minutes"])

        # Ensure monotonic increase: seedling < bud < bloom < queen
        if not (sm < bm < blm < qm):
            print("Warning: Invalid time thresholds order in config; adjusting to monotonic increasing values")
            bm = max(bm, sm + 1)
            blm = max(blm, bm + 1)
            qm = max(qm, blm + 1)
            # Cap to 1440
            bm = min(bm, 1440)
            blm = min(blm, 1440)
            qm = min(qm, 1440)

        base["time_thresholds"] = {
            "seedling_minutes": sm,
            "bud_minutes": bm,
            "bloom_minutes": blm,
            "queen_minutes": qm,
        }

        # Validate top-level numeric fields with basic bounds
        try:
            ms = int(base.get("min_session_seconds", DEFAULT_CONFIG["min_session_seconds"]))
            if ms < 1 or ms > 24 * 3600:
                raise ValueError
            base["min_session_seconds"] = ms
        except Exception:
            base["min_session_seconds"] = DEFAULT_CONFIG["min_session_seconds"]

        try:
            db = int(base.get("default_break_minutes", DEFAULT_CONFIG.get("default_break_minutes", 5)))
            if db < 1 or db > 180:
                raise ValueError
            base["default_break_minutes"] = db
        except Exception:
            base["default_break_minutes"] = DEFAULT_CONFIG.get("default_break_minutes", 5)

    return base


def save_config(config):
    """Save configuration to file"""
    try:
        with open(_config_file_for_write(), "w", encoding="utf-8") as f:
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
