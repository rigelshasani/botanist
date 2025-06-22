import sys
import os

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
        # this below will return -> [10:00-11:30 -- 1h 30m]
        return f"{int(self.start_time.hour):02}:{int(self.start_time.minute):02}-{int(self.finish_time.hour):02}:{int(self.finish_time.minute):02} -- {int(time_diff_full_hours):02}h {int(minutes_left_over):02}m"
    
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

# could i survive falling off a plane into water if i made my legs super straight, hardened muscles, expected fully broken legs but survived the impact?
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
            print(f"Session started at {session.start_time}.")


        # handle finish case
        elif(sys.argv[0] == "botanist.py" and sys.argv[1] == "finish"):
            # if the file exists the session has started
            if os.path.exists(".hiddenBotanist"):
                session = Session()
                session.start()
                with open(".hiddenBotanist", "r") as file:
                    startTime = file.read()
                    session.start_time = datetime.datetime.strptime(startTime, "%Y-%m-%d %H:%M:%S.%f")
                session.finish()
                os.remove(".hiddenBotanist")
                if len(sys.argv) == 2:
                    session.save_to_file("/Users/reatleat/Documents/Obsidian Vault/Data-Science-Curriculum/Current Week.md", "\n") #but now where do i get the desc from
                else:
                    session.save_to_file("/Users/reatleat/Documents/Obsidian Vault/Data-Science-Curriculum/Current Week.md", sys.argv[2])
                print(f"Session saved and finished at {session.finish_time}. Congrats on another session!")
            #if it doesnt exist the session has not started
            else:
                print("Session needs to be started first!")
        # handle everything else
        else:
            print("Invalid argument.")
























# mistakes made: 0 instead of None in variable initialization
# function within a class needs self as a parameter within.
# in tests i forgot that tests are supposed to be INDEPENDENT and i need to 
# create a world within the test where everything that happens within the test
# that does not affect the world outside it. 