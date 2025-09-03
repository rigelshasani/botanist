"""
Analytics and reporting functionality for Botanist.
"""

import os
import json
import datetime
from collections import defaultdict


def calculate_total_pause_time(pauses):
    """Calculate the total time spent in pauses"""
    duration = 0
    for i in range(0, len(pauses)):
        if(pauses[i]["finish"] is not None):
            pause_finish_time = datetime.datetime.strptime(pauses[i]["finish"], "%Y-%m-%d %H:%M:%S.%f")
            pause_start_time = datetime.datetime.strptime(pauses[i]["start"], "%Y-%m-%d %H:%M:%S.%f")
            smallDuration = pause_finish_time - pause_start_time
            duration += smallDuration.total_seconds()
        else:
            duration += (datetime.datetime.now() - datetime.datetime.strptime(pauses[i]["start"], "%Y-%m-%d %H:%M:%S.%f")).total_seconds()
    return duration


def analyze_weekly_totals():
    """Analyze and display weekly productivity statistics"""
    path = ".hiddenGarden.json"
    if not os.path.exists(path):
        print(f"{path} not found.")
        return

    with open(path, "r") as f:
        raw = json.load(f)

    sessions = raw.get("sessions", [])
    if not sessions:
        print("No valid sessions found in .hiddenGarden.json")
        return

    # Historical Friday-based weeks (1-10)
    FRIDAY_START_DATE = datetime.datetime(2025, 6, 20)
    friday_days = ["Friday", "Saturday", "Sunday", "Monday", "Tuesday", "Wednesday", "Thursday"]
    
    # New Monday-based weeks (11+)
    MONDAY_START_DATE = datetime.datetime(2025, 9, 1)  # Monday Sep 1st
    monday_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    
    weekly = defaultdict(lambda: defaultdict(lambda: {"hours": 0.0, "count": 0}))

    for s in sessions:
        try:
            start = datetime.datetime.strptime(s["start_time"], "%Y-%m-%d %H:%M:%S")
            duration = s["duration"] / 3600  # seconds to hours
            
            if start < MONDAY_START_DATE:
                # Historical Friday-based weeks (1-10)
                delta_days = (start - FRIDAY_START_DATE).days
                if delta_days < 0:
                    continue
                week_num = delta_days // 7 + 1
                day_index = delta_days % 7
                day_name = friday_days[day_index]
                weekly[week_num][day_name]["hours"] += duration
                weekly[week_num][day_name]["count"] += 1
            else:
                # New Monday-based weeks (11+)
                delta_days = (start - MONDAY_START_DATE).days
                week_num = delta_days // 7 + 11  # Start numbering from Week 11
                day_index = delta_days % 7
                day_name = monday_days[day_index]
                weekly[week_num][day_name]["hours"] += duration
                weekly[week_num][day_name]["count"] += 1
                
        except Exception as e:
            print("Skipping entry:", s)
            print("Reason:", e)

    total_hours = sum(sum(day["hours"] for day in week.values()) for week in weekly.values())
    print(f"\nTotal hours across all weeks: {total_hours:.2f} h")

    for week_num in sorted(weekly.keys()):
        week = weekly[week_num]
        week_total_hours = sum(day["hours"] for day in week.values())
        week_total_sessions = sum(day["count"] for day in week.values())
        
        if week_num <= 10:
            # Historical Friday-based weeks
            print(f"\nWeek {week_num} (Fri-Thu):  {week_total_hours:.2f} h  across {week_total_sessions} session(s)")
            base_date = FRIDAY_START_DATE + datetime.timedelta(days=(week_num - 1) * 7)
            days_to_use = friday_days
        else:
            # New Monday-based weeks  
            print(f"\nWeek {week_num} (Mon-Sun):  {week_total_hours:.2f} h  across {week_total_sessions} session(s)")
            base_date = MONDAY_START_DATE + datetime.timedelta(days=(week_num - 11) * 7)
            days_to_use = monday_days

        for i, day in enumerate(days_to_use):
            this_date = base_date + datetime.timedelta(days=i)
            label = f"{day:<10} ({this_date.strftime('%b %d')})"
            hours = week[day]["hours"]
            count = week[day]["count"]
            bar = "█" * int(hours * 2) if hours > 0 else ""
            print(f"  {label}  {hours:>5.2f} h  {count}x  {bar}")

    print(f"\nTotal hours across all weeks: {total_hours:.2f} h")