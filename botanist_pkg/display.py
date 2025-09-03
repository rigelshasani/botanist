"""
Display utilities for Botanist ASCII art and formatting.
"""

SESSION_STARTED = """
 ____  _____ ____  ____  _  ___  _   _
/ ___|| ____/ ___|| ___|| |/ _ \| \ | |
\___ \|  _| \___ \|___ \| | | | |  \| |
 ___) | |___ ___) |___) | | |_| | |\  |
|____/|_____|____/|____/|_|\___/|_| \_|

 ____  _____  _    ____ _____ _____ ____  
/ ___||_   _|/ \  |  _ \_   _| ____|  _ \ 
\___ \  | | / _ \ | |_) || | |  _| | | | |
 ___) | | |/ ___ \|  _ < | | | |___| |_| |
|____/  |_/_/   \_\_| \_\|_| |_____|____/ 
"""

FINISHED = """
 _____ ___ _   _ ___ ____  _   _ _____ ____  
|  ___|_ _| \ | |_ _/ ___|| | | | ____|  _ \ 
| |_   | ||  \| || |\___ \| |_| |  _| | | | |
|  _|  | || |\  || | ___) |  _  | |___| |_| |
|_|   |___|_| \_|___|____/|_| |_|_____|____/ 
"""


def print_session_started():
    """Print ASCII art for session start"""
    print(SESSION_STARTED)


def print_session_finished(duration_minutes):
    """Print ASCII art for session completion with duration"""
    hours = duration_minutes // 60
    minutes = duration_minutes % 60
    
    if hours > 0:
        duration_text = f"Duration: {hours}h {minutes}m"
    else:
        duration_text = f"Duration: {minutes}m"
    
    print(FINISHED)
    print(f"            {duration_text.center(20)}")


def print_box(flower):
    """Print a flower surrounded by a decorative box"""
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