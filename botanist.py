import sys
import os

import json
import datetime
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

def assign_flower(duration, streak=0):
    if duration < 1500:
        return "      _\n     (_)\n      |"
    elif duration < 2700:
        return "(@)\n | "
    elif duration < 3600:
        return " .-. \n( + )\n |*| "
    else:
        return """        
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

if __name__ == "__main__":
    # code here runs when script is executed
    if(len(sys.argv) < 2 or len(sys.argv) > 3):
        print("Sorry! Command invalid.")    
    else:
        # handle start case
        if(sys.argv[0] == "botanist.py" and sys.argv[1] == "start"):
            session = Session()
            session.start()
            with open(".hiddenBotanist", "w") as file:
                file.write(str(session.start_time))
            print(f"Session started at {session.start_time.strftime('%A %m/%d %H:%M:%S')}")

        # handle finish case
        elif(sys.argv[0] == "botanist.py" and sys.argv[1] == "finish"):
            # if the file exists the session has started
            if os.path.exists(".hiddenBotanist"):
                session = Session()
                with open(".hiddenBotanist", "r") as file:
                    startTime = file.read()
                    session.start_time = datetime.datetime.strptime(startTime, "%Y-%m-%d %H:%M:%S.%f")
                session.finish()
                os.remove(".hiddenBotanist")
                # cancel session if its short(testing or accidental)
                if (session.finish_time - session.start_time).total_seconds() < 30:
                    print("Session will not be saved. Too short. Try harder.")
                else:
                    my_garden = open_or_create_garden()
                    session.save_to_file("/Users/reatleat/Documents/Obsidian Vault/Data-Science-Curriculum/Current Week.md", sys.argv[2] if len(sys.argv) > 2 else "\n") #but now where do i get the desc from
                    garden_dict = {"date" : session.start_time.strftime("%Y-%m-%d"), "duration": (session.finish_time - session.start_time).total_seconds(), "description" : sys.argv[2] if len(sys.argv) > 2 else "None provided.", "flower" : assign_flower((session.finish_time - session.start_time).total_seconds())}
                    my_garden["sessions"].append(garden_dict)
                    with open(".hiddenGarden.json", "w") as file:
                        json.dump(my_garden, file)
                    print(f"Session saved and finished at {session.finish_time.strftime('%A %m/%d %H:%M:%S')}. Congrats on another session!")
            #if it doesnt exist the session has not started
            else:
                print("Session needs to be started first!")
        # handle everything else
        elif(sys.argv[0] == "botanist.py" and sys.argv[1] == "status"):
            if os.path.exists(".hiddenBotanist"):
                with open(".hiddenBotanist", "r") as file:
                    date = file.read()
                    start_time = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S.%f")
                    duration = datetime.datetime.now() - start_time
                    flower = assign_flower(duration.total_seconds())
                    print(flower)
            else:
                print("Cannot show status of inexistent session. Create session first.")
        # Garden time!
        elif(sys.argv[1] == "garden"):
            my_garden = open_or_create_garden()
            print("Your current streak is: " + str(my_garden["current_streak"]) + " days.")
            for i in my_garden["sessions"]:
                for j in i:
                    if(j == "flower"):
                        print(j + " : ")
                        print("\n")
                        print("---------------")
                        print("\n\n")
                        print(str(i[j]))
                        print("\n\n")
                        print("---------------")
                    elif(j == "duration"):
                        seconds = i[j]
                        minutes = round(seconds/60)
                        print(j + " : " + f"{minutes}")
                    else:
                        print(j + " : " + str(i[j]))
        
        else:
            print("Invalid argument.")
