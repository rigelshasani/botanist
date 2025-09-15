"""
Botanist - A CLI time tracker that grows an ASCII garden.

Main module containing the command-line interface and core application logic.
Tracks work sessions and rewards users with beautiful ASCII flowers based on duration.
"""

import sys
import os
import json
import datetime
import argparse
from pathlib import Path

from botanist_pkg.session import Session
from botanist_pkg.flowers import assign_flower
from botanist_pkg.display import print_box, print_session_started, print_session_finished
from botanist_pkg.analytics import calculate_total_pause_time, analyze_weekly_totals
from botanist_pkg.garden import open_or_create_garden, export_garden_to_csv, add_session_safely, delete_last_session
from botanist_pkg.config import get_min_session_seconds, load_config, update_time_thresholds
from botanist_pkg.utils import sanitize_description
from botanist_pkg.goals import (display_daily_progress, display_weekly_progress, 
                               check_goal_achievements, set_weekly_goal)
from botanist_pkg.paths import (
    active_session_file_for_read,
    active_session_file_for_write,
)


def main(argv=None):
    """
    Main entry for Botanist CLI with argparse subcommands.
    Preserves legacy forms like `config weekly=25` and `finish <desc>`.
    """
    if argv is None:
        argv = sys.argv

    parser = argparse.ArgumentParser(prog="botanist", add_help=True)
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("start")
    sub.add_parser("pause")
    sub.add_parser("resume")
    sub.add_parser("status")
    sub.add_parser("garden")
    sub.add_parser("weekly")
    sub.add_parser("export")
    sub.add_parser("verify")
    sub.add_parser("delete")
    sub.add_parser("test")
    # Missing parser caused documented `goals` command to error
    sub.add_parser("goals")

    p_finish = sub.add_parser("finish")
    p_finish.add_argument("description", nargs="?", default="", help="Optional session description")
    p_finish.add_argument("--desc", "-d", dest="desc", default=None, help="Optional session description")

    p_config = sub.add_parser("config")
    # Legacy support: positional token like weekly=25
    p_config.add_argument("param", nargs="?", default=None)
    # Preferred new form
    p_config.add_argument("--weekly", type=int, dest="weekly_hours", help="Set weekly goal (hours)")

    args = parser.parse_args(argv[1:])
    if not args.command:
        parser.print_help()
        return

    # Command: test - Display sample flowers for different durations
    if args.command == "test":
        print("Testing all flowers:\n")
        print("< 25 min:")
        print_box(assign_flower(1000))  # ~16.7 minutes
        print("\n25-45 min:")
        print_box(assign_flower(2000))  # ~33.3 minutes
        print("\n45-60 min:")
        print_box(assign_flower(3000))  # ~50 minutes
        print("\n60+ min:")
        print_box(assign_flower(4000))  # ~66.7 minutes
            
    # Command: start - Begin a new work session
    elif(args.command == "start"):
        # Check if session already in progress (prevent duplicates)
        if active_session_file_for_read().exists():
            print("Session already started. Use `finish` first.")
            sys.exit()
        else:
            # Create new session and record start time
            session = Session()
            session.start()
            
            # Create temporary session file to track active session
            json_structure ={
                                "session_start": str(session.start_time),
                                "pauses": []  # Track any pause/resume events
                            }
            with open(active_session_file_for_write(), "w") as file:
                json.dump(json_structure, file)
                
            # Display success message with ASCII art
            print_session_started()
            print(f"Session started at {session.start_time.strftime('%A %m/%d %H:%M:%S')}")

    # Command: finish - Complete current session and save to garden
    elif(args.command == "finish"):
        # if the file exists the session has started
        if active_session_file_for_read().exists():
            session = Session()
            with open(active_session_file_for_read(), "r") as file:
                currentSessionInfo = json.load(file)
                session.start_time = datetime.datetime.strptime(currentSessionInfo["session_start"], "%Y-%m-%d %H:%M:%S.%f")
                if currentSessionInfo["pauses"] and currentSessionInfo["pauses"][-1]["finish"] is None:
                    print("You are currently paused. Cannot finish session without unpausing.")
                else:
                    session.finish()
                    # cancel session if its short(testing or accidental)
                    pauseTime = calculate_total_pause_time(currentSessionInfo["pauses"])
                    min_session_time = get_min_session_seconds()
                    if (session.finish_time - session.start_time).total_seconds() - pauseTime < min_session_time:
                        print("Session will not be saved. Too short. Try harder.")
                        # Remove active session marker only after decision
                        try:
                            p = active_session_file_for_read()
                            if p.exists():
                                p.unlink()
                        except Exception:
                            pass
                    else:
                        my_garden = open_or_create_garden()
                        # Sanitize description input
                        raw_description = args.desc if args.desc is not None else args.description
                        clean_description = sanitize_description(raw_description)
                        
                        obsidian_path = os.environ.get('BOTANIST_OBSIDIAN_PATH')
                        if obsidian_path:
                            # Attempt Obsidian write, but don't block saving
                            try:
                                session.save_to_file(obsidian_path, clean_description)
                            except Exception as e:
                                print(f"[WARNING] Failed to write to Obsidian file: {e}")
                        # Create new session data
                        session_data = {
                            "date": session.start_time.strftime("%Y-%m-%d"), 
                            "start_time": session.start_time.strftime("%Y-%m-%d %H:%M:%S"),
                            "end_time": session.finish_time.strftime("%Y-%m-%d %H:%M:%S"),
                            "duration": (session.finish_time - session.start_time).total_seconds() - pauseTime, 
                            "description": clean_description, 
                            "flower": assign_flower((session.finish_time - session.start_time).total_seconds() - pauseTime)
                        }
                        
                        # Use safe append-only operation
                        if add_session_safely(session_data):
                            print("[DATA] Session saved safely with backup")
                            # Remove active session marker after successful save
                            try:
                                p = active_session_file_for_read()
                                if p.exists():
                                    p.unlink()
                            except Exception:
                                pass
                        else:
                            print("[ERROR] Failed to save session data!")
                            return
                        
                        # Show finish message with duration
                        session_duration_minutes = round(((session.finish_time - session.start_time).total_seconds() - pauseTime) / 60)
                        print_session_finished(session_duration_minutes)
                        print(f"Session saved and finished at {session.finish_time.strftime('%A %m/%d %H:%M:%S')}. Congrats on another session!")
                        
                        # Reload garden data and check for goal achievements
                        updated_garden = open_or_create_garden()
                        check_goal_achievements(updated_garden["sessions"], show_celebrations=True)
        #if it doesnt exist the session has not started
        else:
            print("Session needs to be started first!")
    # handle everything else
    elif(args.command == "status"):
        if active_session_file_for_read().exists():
            with open(active_session_file_for_read(), "r") as file:
                currentSessionInfo = json.load(file)
                start_time = datetime.datetime.strptime(currentSessionInfo["session_start"], "%Y-%m-%d %H:%M:%S.%f")
                pauseTime = calculate_total_pause_time(currentSessionInfo["pauses"])
                duration = (datetime.datetime.now() - start_time).total_seconds() - pauseTime
                flower = assign_flower(duration)
                if(duration < 60.0):
                    print(f"Session: {round(duration + pauseTime)} seconds ({round(duration)} seconds working, {round(pauseTime)} seconds paused)")
                else:
                    print(f"Session: {(duration + pauseTime) // 60 } minutes ({duration // 60} minutes working, {pauseTime // 60} minutes paused)")
                print_box(flower)
        else:
            print("Cannot show status of inexistent session. Create session first.")
    # Garden time!
    elif(args.command == "garden"):
        my_garden = open_or_create_garden()
        print("Your current streak is: " + str(my_garden["current_streak"]) + " days.")
        for i in my_garden["sessions"]:
            for j in i:
                if(j == "flower"):
                    print_box(flower=i[j])
                elif(j == "duration"):
                    seconds = i[j]
                    minutes = round(seconds/60)
                    print(j + " : " + f"{minutes} minutes")
                elif(j == "start_time" or j == "end_time"):
                    # Format times nicely for display
                    time_obj = datetime.datetime.strptime(i[j], "%Y-%m-%d %H:%M:%S")
                    print(j + " : " + time_obj.strftime("%a %m/%d %H:%M"))
                else:
                    print(j + " : " + str(i[j]))
    # Pause time
    elif(args.command == "pause"):
        if active_session_file_for_read().exists():
            with open(active_session_file_for_read(), "r") as file:
                currentSessionInfo = json.load(file)
                pauseTime = datetime.datetime.now()
                currentSessionInfo["pauses"].append({"start": str(pauseTime), "finish": None})
                with open(active_session_file_for_write(), "w") as file:
                    json.dump(currentSessionInfo, file)
            # Use configured default break length for suggestion
            try:
                cfg = load_config()
                break_minutes = int(cfg.get("default_break_minutes", 5))
            except Exception:
                break_minutes = 5
            print(
                "You have paused your session. Come back when you feel ready. "
                f"Based on your study duration, I recommend -- {break_minutes} minutes break."
            )
        else:
            print("Session needs to be started first!")
    
    elif(args.command == "resume"):
        if active_session_file_for_read().exists():
            with open(active_session_file_for_read(), "r") as file:
                currentSessionInfo = json.load(file)
                if currentSessionInfo["pauses"]: # empty lists are false in python
                    if(currentSessionInfo["pauses"][-1]["finish"] is None):
                        pauseTime = currentSessionInfo["pauses"][-1]["start"]
                        resumeTime = datetime.datetime.now()
                        start_time = datetime.datetime.strptime(pauseTime, "%Y-%m-%d %H:%M:%S.%f")
                        pauseDuration = resumeTime - start_time
                        currentSessionInfo["pauses"][-1]["finish"] = str(resumeTime)
                        with open(active_session_file_for_write(), "w") as file:
                            json.dump(currentSessionInfo, file)
                        print(f"You successfully unpaused. You were away for {round(pauseDuration.total_seconds() // 60)} minutes. Keep working!")
                    else:
                        print("You cannot resume a session you have not paused first.")
                else:
                    print("You cannot resume a session that is not paused.")
        else:
            print("Cannot resume session that does not exist. Create one first.")

    elif args.command == "weekly":
        analyze_weekly_totals()

    elif(args.command == "export"):
        export_garden_to_csv()
    
    elif(args.command == "config"):
        if args.weekly_hours is None and not args.param:
            # Show current configuration
            config = load_config()
            print("Current Configuration:")
            print(f"  Seedling threshold: {config['time_thresholds']['seedling_minutes']} minutes")
            print(f"  Bud threshold: {config['time_thresholds']['bud_minutes']} minutes") 
            print(f"  Bloom threshold: {config['time_thresholds']['bloom_minutes']} minutes")
            print(f"  Queen threshold: {config['time_thresholds']['queen_minutes']} minutes")
            print(f"  Minimum session: {config['min_session_seconds']} seconds")
            print()
            from botanist_pkg.goals import display_goals_settings
            display_goals_settings()
        elif args.param and isinstance(args.param, str) and args.param.startswith("weekly="):
            # Set weekly goal
            try:
                hours = int(args.param.split("=")[1])
                minutes = hours * 60
                if set_weekly_goal(minutes=minutes):
                    print(f"Weekly goal set to {hours} hours ({minutes} minutes)")
                else:
                    print("Failed to set weekly goal")
            except (ValueError, IndexError):
                print("Usage: config weekly=HOURS")
        elif args.weekly_hours is not None:
            hours = args.weekly_hours
            minutes = hours * 60
            if set_weekly_goal(minutes=minutes):
                print(f"Weekly goal set to {hours} hours ({minutes} minutes)")
            else:
                print("Failed to set weekly goal")
        else:
            print("Usage:")
            print("  config           - View current settings")
            print("  config weekly=N  - Set weekly goal to N hours")
            print("  config --weekly N - Set weekly goal to N hours (preferred)")
    
    elif(args.command == "goals"):
        my_garden = open_or_create_garden()
        sessions = my_garden.get("sessions", [])
        
        # Show today's and this week's progress
        display_daily_progress(sessions)
        display_weekly_progress(sessions)
    
    elif(args.command == "verify"):
        from botanist_pkg.data_protection import verify_data_integrity, list_backups
        print("╔════════════════════════════════════════╗")
        print("║           DATA VERIFICATION            ║")
        print("╚════════════════════════════════════════╝")
        print()
        verify_data_integrity()
        print()
        list_backups()
    
    elif(args.command == "delete"):
        delete_last_session()
    
    else:
        print("Invalid argument.")


if __name__ == "__main__":
    main()
