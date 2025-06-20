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

            pass
        return f"{int(time_diff_full_hours)}h {int(minutes_left_over)}m"

    
    # Now what? 
    # Hint: time_diff.total_seconds() gives you total seconds
    # How do you convert seconds to hours and minutes?


# mistakes made: 0 instead of None in variable initialization
# function within a class needs self as a parameter within.
# in tests i forgot that tests are supposed to be INDEPENDENT and i need to 
# create a world within the test where everything that happens within the test
# that does not affect the world outside it. 