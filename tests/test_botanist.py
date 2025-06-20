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
    assert duration == "1h 30m"# What should 1h 30m equal?



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