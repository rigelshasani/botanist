"""
Goals and target management for Botanist.
"""

import json
import os
import datetime
from collections import defaultdict
from .paths import goals_file_for_read, goals_file_for_write


def _goals_file_for_read() -> str:
    return str(goals_file_for_read())

def _goals_file_for_write() -> str:
    return str(goals_file_for_write())

DEFAULT_GOALS = {
    "weekly": {
        "target_minutes": 1500,  # 25 hours default
        "enabled": True
    }
}


def load_goals():
    """Load goals from file or return defaults."""
    if os.path.exists(_goals_file_for_read()):
        try:
            with open(_goals_file_for_read(), "r") as f:
                goals = json.load(f)
                # Merge with defaults to ensure all keys exist
                merged_goals = DEFAULT_GOALS.copy()
                for key in merged_goals:
                    if key in goals:
                        merged_goals[key].update(goals[key])
                return merged_goals
        except (json.JSONDecodeError, IOError):
            print(f"Warning: Could not load goals file, using defaults")
    
    return DEFAULT_GOALS.copy()


def save_goals(goals):
    """Save goals to file."""
    try:
        with open(_goals_file_for_write(), "w") as f:
            json.dump(goals, f, indent=2)
        return True
    except IOError as e:
        print(f"Error saving goals: {e}")
        return False




def set_weekly_goal(minutes=None):
    """Set weekly time goal in minutes."""
    goals = load_goals()
    
    if minutes is not None:
        if 60 <= minutes <= 3360:  # 1 hour to 56 hours (8h/day)
            goals["weekly"]["target_minutes"] = minutes
        else:
            print("Weekly minutes goal must be between 60 and 3360 (56 hours)")
            return False
    
    return save_goals(goals)


def calculate_daily_progress(sessions, target_date=None):
    """Calculate progress toward daily goals for a specific date."""
    if target_date is None:
        target_date = datetime.date.today()
    elif isinstance(target_date, str):
        target_date = datetime.datetime.strptime(target_date, "%Y-%m-%d").date()
    
    target_date_str = target_date.strftime("%Y-%m-%d")
    
    # Filter sessions for target date
    daily_sessions = [s for s in sessions if s.get("date") == target_date_str]
    
    total_minutes = sum(s.get("duration", 0) / 60 for s in daily_sessions)
    total_sessions = len(daily_sessions)
    
    return {
        "date": target_date_str,
        "minutes": round(total_minutes),
        "sessions": total_sessions,
        "session_list": daily_sessions
    }


def calculate_weekly_progress(sessions, target_week=None):
    """Calculate progress toward weekly goals for a specific week."""
    if target_week is None:
        today = datetime.date.today()
        # Calculate start of current week (Monday)
        days_since_monday = today.weekday()
        week_start = today - datetime.timedelta(days=days_since_monday)
    else:
        week_start = target_week
    
    week_end = week_start + datetime.timedelta(days=6)
    
    # Filter sessions for target week
    weekly_sessions = []
    for s in sessions:
        try:
            session_date = datetime.datetime.strptime(s.get("date", ""), "%Y-%m-%d").date()
            if week_start <= session_date <= week_end:
                weekly_sessions.append(s)
        except ValueError:
            continue
    
    total_minutes = sum(s.get("duration", 0) / 60 for s in weekly_sessions)
    total_sessions = len(weekly_sessions)
    
    # Group by day for detailed view
    daily_breakdown = defaultdict(lambda: {"minutes": 0, "sessions": 0})
    for s in weekly_sessions:
        date = s.get("date", "")
        daily_breakdown[date]["minutes"] += s.get("duration", 0) / 60
        daily_breakdown[date]["sessions"] += 1
    
    return {
        "week_start": week_start.strftime("%Y-%m-%d"),
        "week_end": week_end.strftime("%Y-%m-%d"), 
        "minutes": round(total_minutes),
        "sessions": total_sessions,
        "daily_breakdown": dict(daily_breakdown),
        "session_list": weekly_sessions
    }


def display_daily_progress(sessions, target_date=None):
    """Display today's progress summary."""
    progress = calculate_daily_progress(sessions, target_date)
    
    print("╔════════════════════════════════════════╗")
    print("║            TODAY'S PROGRESS            ║")
    print("╚════════════════════════════════════════╝")
    print()
    print(f"📅 {progress['date']}")
    print(f"⏱️  Focus Time: {progress['minutes']} minutes ({progress['minutes']/60:.1f} hours)")
    print(f"🎯 Sessions: {progress['sessions']} completed")
    print()


def display_weekly_progress(sessions, target_week=None):
    """Display weekly time goal progress with detailed breakdown."""
    goals = load_goals()
    progress = calculate_weekly_progress(sessions, target_week)
    weekly_goals = goals["weekly"]

    # Calculate progress percentage for minutes only
    minutes_progress = (progress["minutes"] / max(1, weekly_goals["target_minutes"])) * 100

    print("╔════════════════════════════════════════╗")
    print("║           WEEKLY PROGRESS              ║")
    print("╚════════════════════════════════════════╝")
    print()
    print(f"📅 Week: {progress['week_start']} to {progress['week_end']}")
    print()

    # Minutes progress bar
    print(f"⏱️  Focus Time: {progress['minutes']}/{weekly_goals['target_minutes']} minutes ({minutes_progress:.0f}%)")
    minutes_bar = create_progress_bar(minutes_progress)
    print(f"   {minutes_bar}")
    print()

    # Daily breakdown
    if progress["daily_breakdown"]:
        print("Daily Breakdown:")
        week_start = datetime.datetime.strptime(progress["week_start"], "%Y-%m-%d").date()

        for i in range(7):
            current_day = week_start + datetime.timedelta(days=i)
            date_str = current_day.strftime("%Y-%m-%d")
            day_name = current_day.strftime("%A")

            if date_str in progress["daily_breakdown"]:
                day_data = progress["daily_breakdown"][date_str]
                minutes = round(day_data["minutes"])
                sessions = day_data["sessions"]
                bar = "█" * min(int(minutes / 20), 20)  # Scale: 20min = 1 block, max 20 blocks
                print(f"  {day_name:<9} {minutes:>3}m {sessions}s {bar}")
            else:
                print(f"  {day_name:<9}   0m 0s")

    print()

    # Achievement status (minutes-only)
    if minutes_progress >= 100:
        print("🏆 Weekly time goal achieved! Outstanding dedication!")
    else:
        remaining_minutes = max(0, weekly_goals["target_minutes"] - progress["minutes"])
        print(f"📈 Keep going! Need {remaining_minutes} more minutes.")
    print()


def create_progress_bar(percentage, width=30):
    """Create a visual progress bar."""
    filled = int((percentage / 100) * width)
    bar = "█" * filled + "░" * (width - filled)
    
    if percentage >= 100:
        return f"[{bar}] ✅"
    elif percentage >= 75:
        return f"[{bar}] 🔥"
    elif percentage >= 50:
        return f"[{bar}] 💪"
    elif percentage >= 25:
        return f"[{bar}] 📈"
    else:
        return f"[{bar}] 🌱"


def display_goals_settings():
    """Display current goal settings."""
    goals = load_goals()
    weekly = goals["weekly"]
    
    print(f"Weekly Target: {weekly['target_minutes']} minutes ({weekly['target_minutes']/60:.0f} hours)")
    print()


def check_goal_achievements(sessions, show_celebrations=True):
    """Check if weekly time goal was achieved and show celebrations."""
    goals = load_goals()
    achievements = []
    
    # Check weekly goals
    if goals["weekly"].get("enabled", True):
        progress = calculate_weekly_progress(sessions)
        weekly_goals = goals["weekly"]

        minutes_achieved = progress["minutes"] >= weekly_goals["target_minutes"]

        if minutes_achieved:
            achievements.append("🏆 Weekly time goal achieved!")
    
    # Show achievements
    if achievements and show_celebrations:
        print()
        for achievement in achievements:
            print(achievement)
        print()
    
    return achievements
