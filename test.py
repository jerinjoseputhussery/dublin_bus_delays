

# Import module
import os
from datetime import datetime
import calendar
import pyodbc
from static_loader_config import connection_string
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
def connection():
    conn = pyodbc.connect(connection_string)
    cursor = conn.cursor()
    cursor.close()
    conn.close()
    if(conn):
        print('Connection is available')
    else:
        print('Connection is not available')
      
# print(dayOfWeek(datetime.now()))
connection()