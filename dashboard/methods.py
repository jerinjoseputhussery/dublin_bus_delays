from config import connection_string
import pyodbc
import pandas as pd
from datetime import datetime
import json
def giveMeRoutes():
    conn = pyodbc.connect(connection_string)
    cursor = conn.cursor()  
    cursor.execute('select * from route_mapping where is_active=1')
    routes = cursor.fetchall() 
    dict ={}
    for row in routes:
        dict[row[1]]=row[0]
    return dict
def giveAllRouteIds(route_short_name):
    conn = pyodbc.connect(connection_string)
    cursor = conn.cursor()  
    cursor.execute('select route_id from route_mapping where route_short_name=?',route_short_name)
    routes = cursor.fetchall() 
    route_ids =[]
    for row in routes:
        route_ids.append(row[0])
    return tuple(route_ids)
def giveRoute_short_name(route_id):
    conn = pyodbc.connect(connection_string)
    cursor = conn.cursor()  
    cursor.execute('select route_short_name from route_mapping where route_id=?',route_id)
    routes = cursor.fetchone()     
    return routes[0]
def reverseRoute(route_title):
    route_title_parts = route_title.split('-')
    reversed_title_parts = list(reversed(route_title_parts))
    reversed_title = ''
    for part in reversed_title_parts:
        if(reversed_title==''):
            reversed_title=part
        else:
            reversed_title=reversed_title+'-'+part
    return reversed_title
def giveMeRouteNamesWithDir():
    conn = pyodbc.connect(connection_string)
    cursor = conn.cursor()  
    cursor.execute('select * from routes where route_id in (select route_id from route_mapping where is_active=1)')
    routes = cursor.fetchall() 
    dict ={}
    for row in routes:
        dict[row[2]+'~1']=row[3]  
        dict[row[2]+'~0']=reverseRoute(row[3])
    return dict
def giveMeRouteName(route_short_name):
    conn = pyodbc.connect(connection_string)
    cursor = conn.cursor()  
    cursor.execute('select * from routes where route_id in (select route_id from route_mapping where is_active=1 and route_short_name=?)',route_short_name)
    routes = cursor.fetchall() 
    dict ={}
    for row in routes:
        dict['1']=row[3]  
        dict['0']=reverseRoute(row[3])
    return dict
def giveMeDFs(res):
    array1 = []
    array2 = []
    for row in res:
        array1.append(row[0])
        array2.append(row[1]) 
    df = pd.DataFrame(dict(
        x = array1,
        y = array2
    )) 
    return df
def giveMe4DFs(res):
    array1 = []
    array2 = []
    array3 = []
    array4 = []
    for row in res:
        array1.append(row[0])
        array2.append(row[1]) 
        array3.append(row[2])
        array4.append(row[3]) 
    df = pd.DataFrame(dict(
        x = array1,
        y = array2,
        z = array3,
        a = array4
    )) 
    return df
def top10routes(todayOrAllTime):
    conn = pyodbc.connect(connection_string)
    cursor = conn.cursor()  
    if(todayOrAllTime=='Today'):
        cursor.execute('select TOP 10 route_id,AVG(current_delay) as avg_delay  from route_delays where CONVERT(date, entry_timestamp)=CONVERT(date, GETDATE()) group by route_id order by avg_delay desc')
    else:
        cursor.execute('select TOP 10 route_id,AVG(current_delay) as avg_delay  from route_delays group by route_id order by avg_delay desc')
    routes = cursor.fetchall() 
    dict ={}
    for row in routes:
        if(giveRoute_short_name(row[0]) in dict):
            if(dict[giveRoute_short_name(row[0])]>row[1]):            
                continue
        dict[giveRoute_short_name(row[0])]=row[1]
    list_to_return = []
    i=0
    for key in dict:
        i=i+1
        list_to_return.append({'SlNo':i,'Route':key,'Route Name':giveMeRouteName(key)['1'],'Average Delays':dict[key]})
    return list_to_return
# print(top10routes('Today'))
def getColors4Times(df):
    colors = ['rgb(166,216,84)',] * df.shape[0]
    colors[df['y'].idxmax()] = 'crimson'  
    return colors
def getColors4Weather(df):
    colors = ['skyblue',] * df.shape[0]
    colors[df['y'].idxmax()] = 'crimson'  
    return colors
def getColors4Day(df):
    colors = ['lightslategray',] * 7
    colors[df['y'].idxmax()] = 'crimson'  
    return colors
def getCurrentWeather():
    conn = pyodbc.connect(connection_string)
    cursor = conn.cursor()  
    cursor.execute('select top 1 w.weather_code,wc.code_description,w.is_day,w.temperature_2m,w.apparent_temperature,w.wind_speed_10m from weather w INNER JOIN weather_codes wc ON w.weather_code=wc.code order by w.entry_id desc')
    return cursor.fetchone()
def getVectorSrc(latest_weather):    
    desc_file = open('assets/descriptions.json')
    descriptions = json.load(desc_file)
    if(latest_weather[2]==1):
        return descriptions[str(latest_weather[0])]['day']['image']
    else:
        return descriptions[str(latest_weather[0])]['night']['image']

