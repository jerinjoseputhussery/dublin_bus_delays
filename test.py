

# Import module
import os
from datetime import datetime
import calendar

# Assign directory
directory = "GTFS_Realtime"
 
# Iterate over files in directory
def iterateFiles():
    for name in os.listdir(directory):
        # Open file
        with open(os.path.join(directory, name)) as f:
            print(name)
            # Read content of file
def dayOfWeek(dt):     
    return calendar.day_name[dt.weekday()]
    
print(dayOfWeek(datetime.now()))