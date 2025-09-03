"""
Session management for time tracking in Botanist.
"""

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
        """Calculate and format the duration between start and finish times"""
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
        """Format session info for Obsidian markdown"""
        return (f"- {self.get_duration()} -- {desc}")

    def save_to_file(self, filename, desc):
        """Save session to an Obsidian markdown file"""
        with open(filename, "r") as file:
            content = file.read()
            
        # Remove trailing newlines to prevent extra spacing
        content = content.rstrip('\n')
        splitContent = content.split('\n')
        
        # Find position before "## Quick Notes" or at the end
        position = None
        for i in range(0, len(splitContent)):
            if splitContent[i] == "## Quick Notes":
                position = i
                break
        
        # If no "## Quick Notes" found, append to end
        if position is None:
            position = len(splitContent)
        
        timeLog = self.format_for_obsidian(desc)
        splitContent.insert(position, timeLog)
        
        # Write back with single trailing newline
        with open(filename, "w") as file:
            joinedContent = '\n'.join(splitContent) + '\n'
            file.write(joinedContent)