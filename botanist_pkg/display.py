"""
Display utilities for Botanist ASCII art and formatting.
"""


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