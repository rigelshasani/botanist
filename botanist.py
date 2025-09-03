"""
Botanist - A CLI time tracker that grows an ASCII garden.

Main module containing the command-line interface and core application logic.
Tracks work sessions and rewards users with beautiful ASCII flowers based on duration.
"""

import sys
import os
import json
import datetime

from botanist_pkg.session import Session
from botanist_pkg.flowers import assign_flower
from botanist_pkg.display import print_box, print_session_started, print_session_finished
from botanist_pkg.analytics import calculate_total_pause_time, analyze_weekly_totals
from botanist_pkg.garden import open_or_create_garden, export_garden_to_csv
from botanist_pkg.config import get_min_session_seconds, load_config, update_time_thresholds
from botanist_pkg.utils import sanitize_description


def main(argv=None):
    """
    Main entry point for Botanist CLI application.
    
    Processes command-line arguments and dispatches to appropriate functionality.
    
    Args:
        argv (list, optional): Command line arguments. Uses sys.argv if None.
        
    Commands:
        start: Begin a new work session
        finish [description]: Complete current session with optional description
        pause: Temporarily pause the current session
        resume: Resume a paused session
        status: Show current session status and progress
        garden: Display all completed sessions
        export: Export session data to CSV
        weekly: Show weekly productivity analysis
        config: Display current configuration
        test: Test flower display system
    """
    if argv is None:
        argv = sys.argv

    # Validate command line arguments
    if len(argv) < 2 or len(argv) > 3:
        print("Sorry! Command invalid.")    
        return
        
    cmd = argv[1]
    
    # Command: test - Display sample flowers for different durations
    if cmd == "test":
        print("Testing all flowers:\n")
        print("< 25 min:")
        print_box(assign_flower(1000))  # 16.7 minutes
        if(cmd == "test"):
            print("Testing all flowers:\n")
            print("< 25 min:")
            print_box(assign_flower(1000))
            
            print("\n25-45 min:")
            print_box(assign_flower(2000))  # 33.3 minutes
            
            print("\n45-60 min:")
            print_box(assign_flower(3000))  # 50 minutes
            
            print("\n60+ min:")
            print_box(assign_flower(4000))  # 66.7 minutes
            
    # Command: start - Begin a new work session
    elif(cmd == "start"):
        # Check if session already in progress (prevent duplicates)
        if os.path.exists(".hiddenBotanist"):
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
            with open(".hiddenBotanist", "w") as file:
                json.dump(json_structure, file)
                
            # Display success message with ASCII art
            print_session_started()
            print(f"Session started at {session.start_time.strftime('%A %m/%d %H:%M:%S')}")

    # Command: finish - Complete current session and save to garden
    elif(cmd == "finish"):
        # if the file exists the session has started
        if os.path.exists(".hiddenBotanist"):
            session = Session()
            with open(".hiddenBotanist", "r") as file:
                currentSessionInfo = json.load(file)
                session.start_time = datetime.datetime.strptime(currentSessionInfo["session_start"], "%Y-%m-%d %H:%M:%S.%f")
                if currentSessionInfo["pauses"] and currentSessionInfo["pauses"][-1]["finish"] is None:
                    print("You are currently paused. Cannot finish session without unpausing.")
                else:
                    session.finish()
                    os.remove(".hiddenBotanist")
                    # cancel session if its short(testing or accidental)
                    pauseTime = calculate_total_pause_time(currentSessionInfo["pauses"])
                    min_session_time = get_min_session_seconds()
                    if (session.finish_time - session.start_time).total_seconds() - pauseTime < min_session_time:
                        print("Session will not be saved. Too short. Try harder.")
                    else:
                        my_garden = open_or_create_garden()
                        # Sanitize description input
                        raw_description = sys.argv[2] if len(sys.argv) > 2 else ""
                        clean_description = sanitize_description(raw_description)
                        
                        obsidian_path = os.environ.get('BOTANIST_OBSIDIAN_PATH')
                        if obsidian_path:
                            session.save_to_file(obsidian_path, clean_description) 
                        garden_dict = {
                            "date": session.start_time.strftime("%Y-%m-%d"), 
                            "start_time": session.start_time.strftime("%Y-%m-%d %H:%M:%S"),
                            "end_time": session.finish_time.strftime("%Y-%m-%d %H:%M:%S"),
                            "duration": (session.finish_time - session.start_time).total_seconds() - pauseTime, 
                            "description": clean_description, 
                            "flower": assign_flower((session.finish_time - session.start_time).total_seconds() - pauseTime)
                            }
                        my_garden["sessions"].append(garden_dict)
                        with open(".hiddenGarden.json", "w") as file:
                            json.dump(my_garden, file)
                        
                        # Show finish message with duration
                        session_duration_minutes = round(((session.finish_time - session.start_time).total_seconds() - pauseTime) / 60)
                        print_session_finished(session_duration_minutes)
                        print(f"Session saved and finished at {session.finish_time.strftime('%A %m/%d %H:%M:%S')}. Congrats on another session!")
        #if it doesnt exist the session has not started
        else:
            print("Session needs to be started first!")
    # handle everything else
    elif(cmd == "status"):
        if os.path.exists(".hiddenBotanist"):
            with open(".hiddenBotanist", "r") as file:
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
    elif(cmd == "garden"):
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
    elif(cmd == "pause"):
        if os.path.exists(".hiddenBotanist"):
            with open(".hiddenBotanist", "r") as file:
                currentSessionInfo = json.load(file)
                pauseTime = datetime.datetime.now()
                currentSessionInfo["pauses"].append({"start": str(pauseTime), "finish": None})
                with open(".hiddenBotanist", "w") as file:
                    json.dump(currentSessionInfo, file)
            print("You have paused your session. Come back when you feel ready. Based on your study duration, I recommend " + "-- 5 minutes break.")
        else:
            print("Session needs to be started first!")
    
    elif(cmd == "resume"):
        if os.path.exists(".hiddenBotanist"):
            with open(".hiddenBotanist", "r") as file:
                currentSessionInfo = json.load(file)
                if currentSessionInfo["pauses"]: # empty lists are false in python
                    if(currentSessionInfo["pauses"][-1]["finish"] is None):
                        pauseTime = currentSessionInfo["pauses"][-1]["start"]
                        resumeTime = datetime.datetime.now()
                        start_time = datetime.datetime.strptime(pauseTime, "%Y-%m-%d %H:%M:%S.%f")
                        pauseDuration = resumeTime - start_time
                        currentSessionInfo["pauses"][-1]["finish"] = str(resumeTime)
                        with open(".hiddenBotanist", "w") as file:
                            json.dump(currentSessionInfo, file)
                        print(f"You successfully unpaused. You were away for {round(pauseDuration.total_seconds() // 60)} minutes. Keep working!")
                    else:
                        print("You cannot resume a session you have not paused first.")
                else:
                    print("You cannot resume a session that is not paused.")
        else:
            print("Cannot resume session that does not exist. Create one first.")

    elif cmd == "weekly":
        analyze_weekly_totals()

    elif(cmd == "export"):
        export_garden_to_csv()
    
    elif(cmd == "config"):
        if len(argv) == 2:
            # Show current configuration
            config = load_config()
            print("Current Configuration:")
            print(f"  Seedling threshold: {config['time_thresholds']['seedling_minutes']} minutes")
            print(f"  Bud threshold: {config['time_thresholds']['bud_minutes']} minutes") 
            print(f"  Bloom threshold: {config['time_thresholds']['bloom_minutes']} minutes")
            print(f"  Queen threshold: {config['time_thresholds']['queen_minutes']} minutes")
            print(f"  Minimum session: {config['min_session_seconds']} seconds")
        else:
            print("Use 'config' to view current settings")
            print("Configuration is stored in .botanist_config.json")
    
    else:
        print("Invalid argument.")


if __name__ == "__main__":
    main()