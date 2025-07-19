import sys
import os

import csv
import json
import datetime
import random

class Session:
    def __init__(self):
        #define start_time with arbitrary value, as it will be overwritten
        self.start_time = None
        self.finish_time = None
        self.time_diff = None
    def start(self):
        self.start_time = datetime.datetime.now()

    def finish(self):
        self.finish_time = datetime.datetime.now()

    def get_duration(self):
        # Calculate the difference
        time_diff = self.finish_time - self.start_time
        time_diff_seconds = time_diff.total_seconds()
        # get full hours
        time_diff_full_hours = time_diff_seconds // 3600
        # get seconds left over using the modulo
        seconds_left_over = time_diff_seconds % 3600
        # convert to minutes left over
        minutes_left_over = seconds_left_over // 60
        # get the final remaining seconds
        seconds_left_over = seconds_left_over - (minutes_left_over * 60)
        if seconds_left_over >= 30:
            if minutes_left_over == 59:
                minutes_left_over = 0
                time_diff_full_hours += 1
            else:
                minutes_left_over += 1
        date_str = self.start_time.strftime("%A %m/%d")
        # this below will return -> [Sunday 22 -- 10:00-11:30 -- 1h 30m]
        return f"{date_str} -- {int(self.start_time.hour):02}:{int(self.start_time.minute):02}-{int(self.finish_time.hour):02}:{int(self.finish_time.minute):02} -- {int(time_diff_full_hours):02}h {int(minutes_left_over):02}m"
    
    def format_for_obsidian(self, desc):
        return (f"- {self.get_duration()} -- {desc}")

    def save_to_file(self, filename, desc):
        with open(filename, "r") as file:
            content = file.read()
            # split file in strings
            splitContent = content.split('\n')
            #find last string before quick notes and add there
            position = None
            for i in range(0, len(splitContent)):
                #handle case where it is found and where its not found
                if splitContent[i] == "## Quick Notes":
                    position = i

            if position == None:
                position = len(splitContent)-1
            timeLog = self.format_for_obsidian(desc)
            with open(filename, "w") as file:
                splitContent.insert(position, timeLog)
                joinedContent = '\n'.join(splitContent)
                file.write(joinedContent)

import random

# Original flowers (keeping these as they are)
SEEDLING = """_
(_)
 |"""

BUD = """(@)
 | """

BLOOM = """ .-. 
( + )
 |*|  """

FULL_BLOOM = """        
        #%:.     
 #%=   ###%=:    
##%=   |##%=:    
##%=   ###%=:    
 #%%=  |##%=:    
 ##%== ###%=:    ===
  ##%%=!##%=:    ====
   ###%%##%=   :==== 
    ######%=: .:==== 
      ####%%======= 
       ###%%%===: 
       |%#%%=:=:  
       ####%=:   
       |##%%:    
-------####%:---=
       |%#%%:    """

# New Eastern-themed symmetric flowers

LOTUS_SMALL = """   .-.   
  ( * )  
   '-'   
    |    """

LOTUS_MEDIUM = """  .--.  
 ( ** ) 
( **** )
 '--'   
   ||   """

LOTUS_LARGE = """   .---.   
  ( *** )  
 ( ***** ) 
( ******* )
  '---'    
    |||    """

CHRYSANTHEMUM = """   ___   
  (o*o)  
 (*o*o*) 
  (o*o)  
   |||   """

PLUM_BLOSSOM = """  .*.  
 *.*.* 
*.*.*.*
 *.*.* 
  .*. 
   |   """

CHERRY_BLOSSOM = """   oOo   
  oOOOo  
 oOOOOOo 
  oOOOo  
   oOo   
    |    """

ORCHID = """  \\ | /  
 - *** - 
  / | \\  
    |    """

PEONY = """  (@@@)  
 (@@@@@) 
(@@@@@@@)
 (@@@@@) 
  (@@@)  
    |    """

BAMBOO_FLOWER = """   |||   
  |*|*|  
 |*|*|*| 
  |*|*|  
   |||   
    |    """

# Special 2+ hour flower
QUEEN_OF_THE_NIGHT = """     .***.     
   .*******.   
  ***********  
 *************
***************
 ************* 
  ***********  
   *******.   
     .***.     
       |       
       |       
 ═══════════════
 Queen of the Night
 ═══════════════"""

def assign_flower(duration, streak=0):
    """Assign flower based on duration with Eastern theme"""
    minutes = duration / 60
    
    # Keep original progression for short sessions
    if minutes < 25:
        return SEEDLING
    elif minutes < 45:
        return BUD
    elif minutes < 60:
        return BLOOM
    elif minutes < 120:
        # For 60-120 minutes, randomly choose from Eastern flowers
        eastern_flowers = [
            LOTUS_SMALL,
            LOTUS_MEDIUM,
            LOTUS_LARGE,
            CHRYSANTHEMUM,
            PLUM_BLOSSOM,
            CHERRY_BLOSSOM,
            ORCHID,
            PEONY,
            BAMBOO_FLOWER,
            FULL_BLOOM  # Include original as one option
        ]
        return random.choice(eastern_flowers)
    else:
        # 2+ hours gets Queen of the Night
        return QUEEN_OF_THE_NIGHT

# Alternative with more control over flower distribution
def assign_flower_weighted(duration, session_number=0):
    """Assign flower with weighted random selection"""
    minutes = duration / 60
    
    if minutes < 25:
        return SEEDLING
    elif minutes < 45:
        return BUD
    elif minutes < 60:
        return BLOOM
    elif minutes < 90:
        # 60-90 minutes: smaller Eastern flowers
        flowers = [LOTUS_SMALL, ORCHID, PLUM_BLOSSOM, CHERRY_BLOSSOM]
        # Use session number for variety but still some randomness
        index = (session_number + random.randint(0, 1)) % len(flowers)
        return flowers[index]
    elif minutes < 120:
        # 90-120 minutes: larger Eastern flowers
        flowers = [LOTUS_LARGE, CHRYSANTHEMUM, PEONY, BAMBOO_FLOWER, FULL_BLOOM]
        index = (session_number + random.randint(0, 1)) % len(flowers)
        return flowers[index]
    else:
        # 2+ hours: Queen of the Night
        return QUEEN_OF_THE_NIGHT

def open_or_create_garden():
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

# GOAL: Put boxes around flowers in garden display
# WHY: Make it visually rewarding
# CURRENT TASK: Add padding to strings
# NEXT: 
def print_box(flower):
    # split the flower into strings
    split_flower = flower.split("\n")
    # create empty array
    lengths = []
    # loop through the split and get the lengths
    for i in split_flower:
        lengths.append(len(i))
    # max value is max length
    max_width = max(lengths)
    # print top box side
    print("╭" + (max_width + 2) * "─" + "╮")
    # print centered line for each of the split lines
    for line in split_flower:
        centered = line.center(max_width + 2)
        print("│" + centered + "│")
    # print bottom box side
    print("╰" + (max_width + 2) * "─" + "╯")

def calculate_total_pause_time(pauses):
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

if __name__ == "__main__":
    # code here runs when script is executed
    if(len(sys.argv) < 2 or len(sys.argv) > 3):
        print("Sorry! Command invalid.")    
    else:
        if(sys.argv[1] == "test"):
            print("Testing all flowers:\n")
            print("< 25 min:")
            print_box(assign_flower(1000))
            
            print("\n25-45 min:")
            print_box(assign_flower(2000))
            
            print("\n45-60 min:")
            print_box(assign_flower(3000))
            
            print("\n60+ min:")
            print_box(assign_flower(4000))
        # handle start case
        elif(sys.argv[1] == "start"):
            if os.path.exists(".hiddenBotanist"):
                print("Session already started. Use `finish` first.")
            else:
                session = Session()
                session.start()
                json_structure ={
                                    "session_start": str(session.start_time),
                                    "pauses": []
                                }
                with open(".hiddenBotanist", "w") as file:
                    json.dump(json_structure, file)
                print(f"Session started at {session.start_time.strftime('%A %m/%d %H:%M:%S')}")

        # handle finish case
        elif(sys.argv[1] == "finish"):
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
                        if (session.finish_time - session.start_time).total_seconds() - pauseTime < 30:
                            print("Session will not be saved. Too short. Try harder.")
                        else:
                            my_garden = open_or_create_garden()
                            obsidian_path = os.environ.get('BOTANIST_OBSIDIAN_PATH')
                            if obsidian_path:
                                session.save_to_file(obsidian_path, sys.argv[2] if len(sys.argv) > 2 else "\n") 
                            garden_dict = {
                                "date": session.start_time.strftime("%Y-%m-%d"), 
                                "start_time": session.start_time.strftime("%Y-%m-%d %H:%M:%S"),
                                "end_time": session.finish_time.strftime("%Y-%m-%d %H:%M:%S"),
                                "duration": (session.finish_time - session.start_time).total_seconds() - pauseTime, 
                                "description": sys.argv[2] if len(sys.argv) > 2 else "None provided.", 
                                "flower": assign_flower((session.finish_time - session.start_time).total_seconds() - pauseTime)
                                }
                            my_garden["sessions"].append(garden_dict)
                            with open(".hiddenGarden.json", "w") as file:
                                json.dump(my_garden, file)
                            print(f"Session saved and finished at {session.finish_time.strftime('%A %m/%d %H:%M:%S')}. Congrats on another session!")
            #if it doesnt exist the session has not started
            else:
                print("Session needs to be started first!")
        # handle everything else
        elif(sys.argv[1] == "status"):
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
        elif(sys.argv[1] == "garden"):
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
        elif(sys.argv[1] == "pause"):
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
        
        elif(sys.argv[1] == "resume"):
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

        elif(sys.argv[1] == "export"):
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
        else:
            print("Invalid argument.")

# %%
