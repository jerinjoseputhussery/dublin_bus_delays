import requests
import json
import pyodbc
from config import api_url,subscription_key
from static_loader_config import database,password,server,username
from getGTFS import download
from static_refresh import refresh
from pushDelays import push_to_delays
import time

def getStaticRoutes():
    conn = pyodbc.connect('DRIVER={SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+password)
    cursor = conn.cursor()
    cursor.execute('SELECT route_id,agency_id,route_short_name,route_long_name FROM [dublin_bus].[dbo].[routes] where agency_id in (select agency_id from agency where agency_name like \'%Dublin Bus%\')')
    rows = cursor.fetchall()
    return rows

def call_api_and_display_response(api_url, headers):
    try:
        # Make a GET request to the API
        response = requests.get(api_url, headers=headers)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Display the API response content
            print("API Response:")
            jsonResponse=json.loads(response.text)
            # print(response.text)
            print('Entity count: ',len(jsonResponse["entity"]))
            noOfDelayEntries=0
            total_arrival_delays=0            
            routesFromDatabase = [row[0] for row in getStaticRoutes()]
            currentRoutes=set()            
            for entities in jsonResponse["entity"]:
                if(entities["trip_update"]["trip"]["schedule_relationship"]=='SCHEDULED'):
                    if(entities["trip_update"]["trip"]["route_id"] in routesFromDatabase):
                        currentRoutes.add(entities["trip_update"]["trip"]["route_id"])                        
                        if("stop_time_update" in entities["trip_update"]):                            
                            for stop_time_update in entities["trip_update"]["stop_time_update"]:
                                # print(stop_time_update)
                                if("arrival" in stop_time_update):
                                    if("delay" in stop_time_update["arrival"]):                                
                                        total_arrival_delays+=stop_time_update["arrival"]["delay"]                                        
                                        noOfDelayEntries+=1
                                elif("departure" in stop_time_update):
                                    if("delay" in stop_time_update["departure"]):                                
                                        total_arrival_delays+=stop_time_update["departure"]["delay"]                                        
                                        noOfDelayEntries+=1
            if(len(currentRoutes)==0):
                print('No current routes matching') 
                download()  
                refresh()             
                return
            # Below are the code to get the delay from all the current routes, the avaerage of delays from all current routes are stored in avgRouteDelays DICTIONARY
            routeDelays = {}
            tripCounts = {}
            avgRouteDelays = {}
            currentRoutesWithDirection=set()
            for route in currentRoutes:
                currentRoutesWithDirection.add(route+'~0')
                currentRoutesWithDirection.add(route+'~1')
            for route in currentRoutesWithDirection:
                routeDelays[route]=0
                tripCounts[route]=0
            for entities in jsonResponse["entity"]:
                if(entities["trip_update"]["trip"]["schedule_relationship"]=='SCHEDULED' and entities["trip_update"]["trip"]["route_id"] in currentRoutes):                    
                    if("stop_time_update" in entities["trip_update"]):
                        total_trip_delay=0
                        noOfTripUpdates=0
                        for stop_time_update in entities["trip_update"]["stop_time_update"]:                            
                            if("arrival" in stop_time_update):
                                if("delay" in stop_time_update["arrival"]):                                
                                    noOfTripUpdates+=1
                                    total_trip_delay+=stop_time_update["arrival"]["delay"] 
                            elif("departure" in stop_time_update):
                                if("delay" in stop_time_update["departure"]):                                
                                    noOfTripUpdates+=1
                                    total_trip_delay+=stop_time_update["departure"]["delay"] 
                        if(noOfTripUpdates>0):                            
                            avg_trip_delay=int(total_trip_delay/noOfTripUpdates)
                            if(entities["trip_update"]["trip"]["direction_id"]==0):
                                routeDelays[entities["trip_update"]["trip"]["route_id"]+'~0']+=avg_trip_delay
                                tripCounts[entities["trip_update"]["trip"]["route_id"]+'~0']+=1
                            elif(entities["trip_update"]["trip"]["direction_id"]==1):
                                routeDelays[entities["trip_update"]["trip"]["route_id"]+'~1']+=avg_trip_delay
                                tripCounts[entities["trip_update"]["trip"]["route_id"]+'~1']+=1
            print('routeDelays: ',routeDelays)
            print('tripCounts: ',tripCounts)            
            for key in routeDelays:
                if(tripCounts[key]>0):
                    avgRouteDelays[key] = int(routeDelays[key]/tripCounts[key])
            
            print('Current',len(currentRoutes),'DUBLIN BUS Routes: ',sorted(currentRoutes))
            avgDelayFromAllRoutes=int(total_arrival_delays/noOfDelayEntries)
            minutes, seconds = divmod(avgDelayFromAllRoutes, 60)
            print(avgDelayFromAllRoutes)
            push_to_delays(jsonResponse["header"]["timestamp"],avgDelayFromAllRoutes,avgRouteDelays)
            print('Average delays from all current routes: ',minutes, ' minutes ',seconds,' seconds')
            print(avgRouteDelays)
            # sum=0
            # for key in avgRouteDelays:
            #     sum+=routeDelays[key]
            # print('Average: ',int(sum/len(avgRouteDelays)))
            # minutes, seconds = divmod(int(sum/len(avgRouteDelays)), 60)
            # print('Average delays from all current routes: ',minutes, ' minutes ',seconds,' seconds')
        else:
            # Display an error message for unsuccessful requests
            print(f"Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"An error occurred: {e}")

start_time = time.time()
headers = {'x-api-key': subscription_key }
call_api_and_display_response(api_url, headers)
print("--- %s seconds ---" % (time.time() - start_time))

