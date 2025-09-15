"""
Platform-aware paths for Botanist data storage.

Moves data from CWD into a stable per-user application dir while
maintaining backward compatibility with legacy files in CWD.
"""

import os
import sys
from pathlib import Path


APP_DIR_WIN = "Botanist"
APP_DIR_MAC = "Botanist"
APP_DIR_LINUX = "botanist"


def get_data_dir() -> Path:
    """Return the per-user data directory for Botanist and ensure it exists."""
    if sys.platform.startswith("win"):
        base = os.getenv("APPDATA")
        if not base:
            base = str(Path.home() / "AppData" / "Roaming")
        data_dir = Path(base) / APP_DIR_WIN
    elif sys.platform == "darwin":
        data_dir = Path.home() / "Library" / "Application Support" / APP_DIR_MAC
    else:
        base = os.getenv("XDG_DATA_HOME")
        if not base:
            base = str(Path.home() / ".local" / "share")
        data_dir = Path(base) / APP_DIR_LINUX

    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


# -------- File getters (new locations) --------

def garden_file_new() -> Path:
    return get_data_dir() / "garden.json"


def active_session_file_new() -> Path:
    return get_data_dir() / "active_session.json"


def backup_dir_new() -> Path:
    d = get_data_dir() / "backups"
    d.mkdir(parents=True, exist_ok=True)
    return d


def goals_file_new() -> Path:
    return get_data_dir() / "goals.json"


def config_file_new() -> Path:
    return get_data_dir() / "config.json"


# -------- Legacy paths (CWD) --------

def garden_file_legacy() -> Path:
    return Path.cwd() / ".hiddenGarden.json"


def active_session_file_legacy() -> Path:
    return Path.cwd() / ".hiddenBotanist"


def backup_dir_legacy() -> Path:
    return Path.cwd() / ".botanist_backups"


def goals_file_legacy() -> Path:
    return Path.cwd() / ".botanist_goals.json"


def config_file_legacy() -> Path:
    return Path.cwd() / ".botanist_config.json"


# -------- Resolvers --------

def resolve_read_path(preferred: Path, legacy: Path) -> Path:
    """Return preferred if it exists, else legacy if it exists, else preferred."""
    if preferred.exists():
        return preferred
    if legacy.exists():
        return legacy
    return preferred


def garden_file_for_read() -> Path:
    return resolve_read_path(garden_file_new(), garden_file_legacy())


def garden_file_for_write() -> Path:
    return garden_file_new()


def active_session_file_for_read() -> Path:
    return resolve_read_path(active_session_file_new(), active_session_file_legacy())


def active_session_file_for_write() -> Path:
    return active_session_file_new()


def backup_dir_for_use() -> Path:
    # Always use the new backup dir
    return backup_dir_new()


def goals_file_for_read() -> Path:
    return resolve_read_path(goals_file_new(), goals_file_legacy())


def goals_file_for_write() -> Path:
    return goals_file_new()


def config_file_for_read() -> Path:
    return resolve_read_path(config_file_new(), config_file_legacy())


def config_file_for_write() -> Path:
    return config_file_new()

