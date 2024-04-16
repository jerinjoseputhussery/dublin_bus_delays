import pyodbc
import json
from datetime import datetime
from static_loader_config import database,password,server,username 
from weather import getCurrentWeather
from config import location
def convert_timestamp(posix_timestamp_str):
    # Convert string POSIX timestamp to integer
    posix_timestamp = int(posix_timestamp_str)    
    # Convert POSIX timestamp to datetime object
    dt_object = datetime.fromtimestamp(posix_timestamp)    
    # Format datetime object as string in MSSQL format
    mssql_datetime = dt_object.strftime('%Y-%m-%d %H:%M:%S')    
    return mssql_datetime

def push_to_delays(timestamp,avgDelayFromAllRoutes,avgRouteDelays):
    conn = pyodbc.connect('DRIVER={SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+password)
    cursor = conn.cursor()
    cursor.execute('select NEXT VALUE FOR entry_id_seq')
    entry_id = cursor.fetchone()[0]
    statement = 'INSERT INTO delays values(?,?,?,?)'
    cursor.execute(statement,(entry_id,convert_timestamp(timestamp),avgDelayFromAllRoutes,0))
    
    for key in avgRouteDelays:
        statement = 'INSERT INTO route_delays values(?,?,?,?,?,?)'
        cursor.execute(statement,(entry_id,key.split('~')[0],key.split('~')[1],convert_timestamp(timestamp),avgRouteDelays[key],0))
    
    #weather
    weather = json.loads(getCurrentWeather())
    statement = 'INSERT INTO weather values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)'
    cursor.execute(statement,(entry_id,location,convert_timestamp(weather["current"]["time"]),weather["current"]["temperature_2m"],weather["current"]["relative_humidity_2m"],weather["current"]["apparent_temperature"]
                              ,weather["current"]["is_day"],weather["current"]["precipitation"],weather["current"]["rain"],weather["current"]["showers"],weather["current"]["snowfall"]
                   ,weather["current"]["weather_code"],weather["current"]["cloud_cover"],weather["current"]["pressure_msl"],weather["current"]["surface_pressure"],weather["current"]["wind_speed_10m"]
                   ,weather["current"]["wind_direction_10m"],weather["current"]["wind_gusts_10m"],0,0,0,0,0,0,0,0,0,0,0,0,0))
    conn.commit()
    cursor.close()
    conn.close()   
    print('Push to database is completed') 