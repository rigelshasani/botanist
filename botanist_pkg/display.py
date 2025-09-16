"""
Display utilities for Botanist ASCII art and formatting.
Includes width-aware centering that handles wide Unicode.
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

import unicodedata

def display_width(text: str) -> int:
    """Compute display cell width for text, approximating wcwidth.

    - Treat combining marks and certain format chars (e.g., ZWJ) as width 0
    - Treat East Asian Wide/Fullwidth as width 2
    - Everything else width 1
    """
    w = 0
    for ch in text:
        # Zero-width if combining or control/format joiner
        if unicodedata.combining(ch):
            continue
        cat = unicodedata.category(ch)
        if cat in ("Cf",):  # format (ZWJ, etc.)
            continue
        ea = unicodedata.east_asian_width(ch)
        if ea in ("W", "F"):
            w += 2
        else:
            w += 1
    return w


def pad_center_by_width(text: str, target_width: int, fillchar: str = " ") -> str:
    """Center text to a target display width using spaces."""
    cur = display_width(text)
    if cur >= target_width:
        return text
    total_pad = target_width - cur
    left = total_pad // 2
    right = total_pad - left
    return (fillchar * left) + text + (fillchar * right)


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
    """Print a flower surrounded by a decorative box with width-aware centering."""
    split_flower = flower.split("\n")
    # Determine max display width across lines
    max_w = 0
    for i in split_flower:
        max_w = max(max_w, display_width(i))
    # Top border
    print("╭" + (max_w + 2) * "─" + "╮")
    # Center each line according to display width
    for line in split_flower:
        centered = pad_center_by_width(line, max_w + 2)
        print("│" + centered + "│")
    # Bottom border
    print("╰" + (max_w + 2) * "─" + "╯")
