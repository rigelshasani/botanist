from botanist import Session

import datetime

def test_start_records_time():
    # Create... something that can track time
    session = Session()
    # Tell it to start
    session.start()
    # Check that it recorded a start time
    assert session.start_time is not None

def test_finish_records_time():
    session = Session()
    session.start()
    session.finish()
    assert session.finish_time is not None

def test_get_duration():
    session = Session()
    session.start()
    #there should be some sort of wait function that simulates a wait
    #or i could manually set session.finish_time to be session.start_time + 5;
    session.start_time = datetime.datetime(2025, 6, 20, 10, 0, 0)  # 10:00:00
    session.finish()
    session.finish_time = datetime.datetime(2025, 6, 20, 11, 30, 0)  # 11:30:00
    # Now what should we assert?
    duration = session.get_duration()
    assert duration == "10:00-11:30 -- 01h 30m"# What should 1h 30m equal?

def test_format_for_obsidian():
    # Create a session
    session = Session()
    # Set its start and end times manually (so we control the values)
    session.start()
    session.start_time = datetime.datetime(2025, 6, 20, 12, 0, 0)
    session.finish()
    session.finish_time = datetime.datetime(2025, 6, 20, 13, 30, 0)
    # Call a method like session.format_for_obsidian("Botanist TDD")
    content = session.format_for_obsidian("Botanist TDD") 
    assert content == "- 12:00-13:30 -- 01h 30m -- Botanist TDD"
    
    # Assert it returns the string: "- 12:00-13:30 -- 1h 30m -- Botanist TDD"

    #Creates a temporary test file with that simple content
def test_add_time_entry():
    with open("filename.txt", "w") as file:
        previousContent = "## Time\n- 10:00-11:00 -- 01h 00m -- Previous work\n## Quick Notes\n- Learned about modulo operator"
        file.write(previousContent)
    #Calls some method to add a time entry
    session = Session()
    session.start()
    session.start_time = datetime.datetime(2025, 6, 20, 12, 0, 0)
    session.finish()
    session.finish_time = datetime.datetime(2025, 6, 20, 13, 30, 0)
    session.save_to_file("filename.txt", "Current Work")
    with open("filename.txt", "r") as file:
        content = file.read()
        assert content == "## Time\n- 10:00-11:00 -- 01h 00m -- Previous work\n- 12:00-13:30 -- 01h 30m -- Current Work\n## Quick Notes\n- Learned about modulo operator"
         

    #Reads the file back and checks it has both entries?


# import datetime

# def test_start_records_time(command):
#     # Create... something that can track time
#     if command == "start":
#         currentTime = datetime()
#         return currentTime
#     else:
#         pass
#     # Tell it to start
#     # Check that it recorded a start time