from config import connection_string
import pyodbc
import pandas as pd
from datetime import datetime
def giveMeRoutes():
    conn = pyodbc.connect(connection_string)
    cursor = conn.cursor()  
    cursor.execute('select * from route_mapping where is_active=1')
    routes = cursor.fetchall() 
    dict ={}
    for row in routes:
        dict[row[1]]=row[0]
    return dict
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

