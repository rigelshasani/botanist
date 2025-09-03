"""
Garden data management for Botanist.
"""

import os
import json
import csv


def open_or_create_garden():
    """Load existing garden data or create a new garden file"""
    # if the garden exists, load it
    if os.path.exists(".hiddenGarden.json"):
        with open(".hiddenGarden.json", "r") as file:
            garden_data = json.load(file)
            return garden_data
    # if it doesn't, create it. 
    else:
        with open(".hiddenGarden.json", "w") as file:
            garden_data = {
                "current_streak": 0,
                "sessions": []
                }
            json.dump(garden_data, file)
            return garden_data


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