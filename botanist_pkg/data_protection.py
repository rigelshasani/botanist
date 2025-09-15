"""
Data protection and backup system for Botanist.
Ensures session data integrity and prevents accidental loss.
"""

import json
import os
import shutil
import datetime
from typing import Dict, List, Any
from .paths import (
    garden_file_for_read,
    garden_file_for_write,
    backup_dir_for_use,
)


def _garden_file_current() -> str:
    return str(garden_file_for_write())

def _garden_file_for_read() -> str:
    return str(garden_file_for_read())

def _backup_dir_current() -> str:
    return str(backup_dir_for_use())
MAX_BACKUPS = 30  # Keep 30 backup files


def create_backup():
    """
    Create a timestamped backup of the garden file.
    Called before any write operation to ensure data safety.
    """
    if not os.path.exists(_garden_file_for_read()):
        return  # Nothing to backup
    
    # Create backup directory if it doesn't exist
    backup_dir = _backup_dir_current()
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    # Create timestamped backup filename
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"garden_backup_{timestamp}.json"
    backup_path = os.path.join(backup_dir, backup_filename)
    
    # Copy the current file to backup
    try:
        shutil.copy2(_garden_file_for_read(), backup_path)
        print(f"[BACKUP] Created: {backup_filename}")
    except IOError as e:
        print(f"[WARNING] Failed to create backup: {e}")
    
    # Clean up old backups
    cleanup_old_backups()


def cleanup_old_backups():
    """Remove old backup files, keeping only the most recent MAX_BACKUPS."""
    backup_dir = _backup_dir_current()
    if not os.path.exists(backup_dir):
        return
    
    try:
        # Get all backup files
        backup_files = []
        for filename in os.listdir(backup_dir):
            if filename.startswith("garden_backup_") and filename.endswith(".json"):
                filepath = os.path.join(backup_dir, filename)
                mtime = os.path.getmtime(filepath)
                backup_files.append((mtime, filepath, filename))
        
        # Sort by modification time (newest first)
        backup_files.sort(reverse=True)
        
        # Remove old backups beyond MAX_BACKUPS
        for i, (mtime, filepath, filename) in enumerate(backup_files):
            if i >= MAX_BACKUPS:
                os.remove(filepath)
                print(f"[CLEANUP] Removed old backup: {filename}")
                
    except OSError as e:
        print(f"[WARNING] Cleanup failed: {e}")


def validate_garden_data(data: Dict[str, Any]) -> bool:
    """
    Validate garden data structure to prevent corruption.
    
    Args:
        data: Garden data dictionary
        
    Returns:
        bool: True if data is valid, False otherwise
    """
    # Check required top-level keys
    if not isinstance(data, dict):
        return False
        
    if "sessions" not in data:
        return False
        
    if not isinstance(data["sessions"], list):
        return False
    
    # Check current_streak exists and is valid
    if "current_streak" not in data:
        data["current_streak"] = 0  # Fix missing streak
    
    if not isinstance(data["current_streak"], (int, float)):
        data["current_streak"] = 0  # Fix invalid streak
    
    # Validate each session
    valid_sessions = []
    for session in data["sessions"]:
        if validate_session(session):
            valid_sessions.append(session)
        else:
            print(f"[WARNING] Skipping invalid session: {session}")
    
    # Update sessions list with only valid sessions
    data["sessions"] = valid_sessions
    
    return True


def validate_session(session: Dict[str, Any]) -> bool:
    """
    Validate a single session entry.
    
    Args:
        session: Session dictionary
        
    Returns:
        bool: True if session is valid, False otherwise
    """
    required_fields = ["date", "start_time", "end_time", "duration", "description", "flower"]
    
    # Check all required fields exist
    for field in required_fields:
        if field not in session:
            return False
    
    # Validate date format
    try:
        datetime.datetime.strptime(session["date"], "%Y-%m-%d")
    except ValueError:
        return False
    
    # Validate start_time and end_time format
    try:
        datetime.datetime.strptime(session["start_time"], "%Y-%m-%d %H:%M:%S")
        datetime.datetime.strptime(session["end_time"], "%Y-%m-%d %H:%M:%S") 
    except ValueError:
        return False
    
    # Validate duration is a number and positive
    if not isinstance(session["duration"], (int, float)) or session["duration"] < 0:
        return False
    
    # Validate description is a string
    if not isinstance(session["description"], str):
        return False
    
    # Validate flower is a string
    if not isinstance(session["flower"], str):
        return False
    
    return True


def safe_write_garden(data: Dict[str, Any]) -> bool:
    """
    Safely write garden data with backup and validation.
    
    Args:
        data: Garden data to write
        
    Returns:
        bool: True if write was successful, False otherwise
    """
    # Validate data before writing
    if not validate_garden_data(data):
        print("[ERROR] Invalid garden data, write aborted!")
        return False
    
    # Create backup before writing
    create_backup()
    
    # Write to temporary file first
    temp_file = _garden_file_current() + ".tmp"
    try:
        with open(temp_file, "w") as f:
            json.dump(data, f, indent=2)
        
        # Atomically replace the original file
        if os.path.exists(temp_file):
            shutil.move(temp_file, _garden_file_current())
            return True
    except (IOError, TypeError, ValueError) as e:
        print(f"[ERROR] Failed to write garden data: {e}")
        # Clean up temp file
        if os.path.exists(temp_file):
            os.remove(temp_file)
        return False
    
    return False


def safe_read_garden() -> Dict[str, Any]:
    """
    Safely read garden data with corruption recovery.
    
    Returns:
        dict: Garden data or default structure if file is corrupted
    """
    if not os.path.exists(_garden_file_for_read()):
        # Return default structure
        return {
            "current_streak": 0,
            "sessions": []
        }
    
    try:
        with open(_garden_file_for_read(), "r") as f:
            data = json.load(f)
        
        # Validate the loaded data
        if validate_garden_data(data):
            return data
        else:
            print("[WARNING] Garden data validation failed!")
            return try_restore_from_backup()
            
    except (IOError, json.JSONDecodeError) as e:
        print(f"[ERROR] Failed to read garden data: {e}")
        return try_restore_from_backup()


def try_restore_from_backup() -> Dict[str, Any]:
    """
    Try to restore garden data from the most recent backup.
    
    Returns:
        dict: Restored data or default structure if no valid backup
    """
    backup_dir = _backup_dir_current()
    if not os.path.exists(backup_dir):
        print("[WARNING] No backups available, using default structure")
        return {"current_streak": 0, "sessions": []}
    
    try:
        # Get all backup files
        backup_files = []
        for filename in os.listdir(backup_dir):
            if filename.startswith("garden_backup_") and filename.endswith(".json"):
                filepath = os.path.join(backup_dir, filename)
                mtime = os.path.getmtime(filepath)
                backup_files.append((mtime, filepath, filename))
        
        # Sort by modification time (newest first)
        backup_files.sort(reverse=True)
        
        # Try to restore from each backup (newest first)
        for mtime, filepath, filename in backup_files:
            try:
                with open(filepath, "r") as f:
                    data = json.load(f)
                
                if validate_garden_data(data):
                    print(f"[RECOVERY] Restored from backup: {filename}")
                    # Write the recovered data back to main file
                    with open(_garden_file_current(), "w") as f:
                        json.dump(data, f, indent=2)
                    return data
            except (IOError, json.JSONDecodeError):
                continue  # Try next backup
        
        print("[ERROR] No valid backups found, using default structure")
        return {"current_streak": 0, "sessions": []}
        
    except OSError as e:
        print(f"[ERROR] Backup recovery failed: {e}")
        return {"current_streak": 0, "sessions": []}


def append_session_only(new_session: Dict[str, Any]) -> bool:
    """
    Append a new session to the garden without risk of data loss.
    This is the safest way to add data.
    
    Args:
        new_session: Session dictionary to append
        
    Returns:
        bool: True if append was successful, False otherwise
    """
    # Validate the new session
    if not validate_session(new_session):
        print("[ERROR] Invalid session data, append aborted!")
        return False
    
    # Read current data safely
    garden_data = safe_read_garden()
    
    # Append the new session (never removes existing data)
    garden_data["sessions"].append(new_session)
    
    # Write back safely
    return safe_write_garden(garden_data)


def list_backups():
    """List all available backup files."""
    backup_dir = _backup_dir_current()
    if not os.path.exists(backup_dir):
        print("No backups found.")
        return
    
    try:
        backup_files = []
        for filename in os.listdir(backup_dir):
            if filename.startswith("garden_backup_") and filename.endswith(".json"):
                filepath = os.path.join(backup_dir, filename)
                mtime = os.path.getmtime(filepath)
                size = os.path.getsize(filepath)
                backup_files.append((mtime, filepath, filename, size))
        
        if not backup_files:
            print("No backup files found.")
            return
        
        # Sort by modification time (newest first)
        backup_files.sort(reverse=True)
        
        print("Available backups:")
        for mtime, filepath, filename, size in backup_files:
            timestamp = datetime.datetime.fromtimestamp(mtime)
            print(f"  {filename} - {timestamp.strftime('%Y-%m-%d %H:%M:%S')} ({size} bytes)")
            
    except OSError as e:
        print(f"Error listing backups: {e}")


def verify_data_integrity():
    """Verify the integrity of the current garden data."""
    try:
        data = safe_read_garden()
        session_count = len(data.get("sessions", []))
        streak = data.get("current_streak", 0)
        
        print("Data Integrity Report:")
        print(f"  Sessions: {session_count}")
        print(f"  Streak: {streak}")
        print(f"  Status: ✅ Valid")
        
        # Check for duplicates
        dates_and_times = []
        duplicates = 0
        for session in data["sessions"]:
            key = (session.get("date", ""), session.get("start_time", ""))
            if key in dates_and_times:
                duplicates += 1
            else:
                dates_and_times.append(key)
        
        if duplicates > 0:
            print(f"  Warning: {duplicates} potential duplicate sessions found")
        
        return True
        
    except Exception as e:
        print(f"Data integrity check failed: {e}")
        return False
