"""
Garden data management for Botanist.
"""

import os
import json
import csv
from .data_protection import safe_read_garden, safe_write_garden, append_session_only


def open_or_create_garden():
    """Load existing garden data or create a new garden file using safe operations"""
    return safe_read_garden()


def save_garden_safely(garden_data):
    """Save garden data using safe write operations with backup"""
    return safe_write_garden(garden_data)


def add_session_safely(new_session):
    """Add a new session using append-only operation (safest method)"""
    return append_session_only(new_session)


def delete_last_session():
    """
    Delete the last session from both temporary session file and garden data.
    
    This function safely removes:
    1. The temporary .hiddenBotanist file if it exists (active session)
    2. The most recent session from .hiddenGarden.json if it exists
    
    Returns:
        bool: True if any deletion occurred, False if nothing to delete
    """
    # Check what would be deleted
    active_session_exists = os.path.exists(".hiddenBotanist")
    garden_data = safe_read_garden()
    has_completed_sessions = (garden_data and "sessions" in garden_data and garden_data["sessions"])
    
    if not active_session_exists and not has_completed_sessions:
        print("[INFO] No active session or completed sessions to delete")
        return False
    
    # Show what will be deleted
    print("╔════════════════════════════════════════╗")
    print("║         DELETION CONFIRMATION          ║")
    print("╚════════════════════════════════════════╝")
    print()
    
    if active_session_exists:
        print("• Active session (.hiddenBotanist) will be deleted")
    
    if has_completed_sessions:
        last_session = garden_data["sessions"][-1]
        print(f"• Last completed session will be deleted:")
        print(f"  Date: {last_session['date']}")
        print(f"  Time: {last_session.get('start_time', 'N/A')}")
        print(f"  Description: {last_session.get('description', 'No description')}")
        print(f"  Duration: {round(last_session.get('duration', 0) / 60)} minutes")
    
    print()
    try:
        confirmation = input("Are you sure you want to delete? Type 'yes' to confirm: ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        print("\n[CANCELLED] Deletion cancelled")
        return False
    
    if confirmation != 'yes':
        print("[CANCELLED] Deletion cancelled by user")
        return False
    
    deleted_something = False
    
    # Step 1: Remove temporary session file if it exists
    if active_session_exists:
        os.remove(".hiddenBotanist")
        print("[DELETED] Removed active session (.hiddenBotanist)")
        deleted_something = True
    
    # Step 2: Remove last session from garden data if it exists
    if has_completed_sessions:
        last_session = garden_data["sessions"][-1]
        
        # Remove the last session
        garden_data["sessions"] = garden_data["sessions"][:-1]
        
        # Save the updated garden data
        if save_garden_safely(garden_data):
            print(f"[DELETED] Removed last session: {last_session['date']} {last_session.get('start_time', 'N/A')} - {last_session.get('description', 'No description')}")
            deleted_something = True
        else:
            print("[ERROR] Failed to save garden data after deletion")
            return False
    
    return deleted_something


def export_garden_to_csv():
    """Export garden data to CSV format"""
    if os.path.exists(".hiddenGarden.json"):
        with open(".hiddenGarden.json", "r") as file:
            gardenInfo = json.load(file)
            # create output file
            with open("exportedGarden.csv", "w") as output:
                # create writer object
                writer = csv.writer(output)
                # create headers
                writer.writerow(["date", "start_time", "end_time", "duration_minutes", "description"])
                for session in gardenInfo["sessions"]:
                    start_time = session.get("start_time", "N/A")
                    end_time = session.get("end_time", "N/A")
                    writer.writerow([
                        session["date"], 
                        start_time,
                        end_time,
                        round(session["duration"] / 60), 
                        session["description"]
                    ])
        print(f"Exported {len(gardenInfo['sessions'])} sessions to exportedGarden.csv")
    else:
        print("Data file does not exist. Start and finish a new session to create it.")