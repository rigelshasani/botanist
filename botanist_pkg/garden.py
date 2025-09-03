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