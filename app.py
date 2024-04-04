import requests
import json
import pyodbc
from config import api_url,subscription_key
from static_loader_config import database,password,server,username

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
            count=0
            total_arrival_delays=0            
            routesFromDatabase = [row[0] for row in getStaticRoutes()]
            currentRoutes=set()
            for entities in jsonResponse["entity"]:
                if(entities["trip_update"]["trip"]["schedule_relationship"]=='SCHEDULED'):                    
                    count+=1
                    if(entities["trip_update"]["trip"]["route_id"] in routesFromDatabase):
                        currentRoutes.add(entities["trip_update"]["trip"]["route_id"])
                    # for stop_time_update in entities["trip_update"]["stop_time_update"]:
                    #     stop_time_update["arrival"]["delay"]
            print('SCHEDULED: ',count)
            print('Current',len(currentRoutes),'DUBLIN BUS Routes: ',currentRoutes)
        else:
            # Display an error message for unsuccessful requests
            print(f"Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"An error occurred: {e}")

# Replace 'your_api_url_here' with the actual API URL you want to call
#api_url = 'your_api_url_here'
headers = {'x-api-key': subscription_key }
call_api_and_display_response(api_url, headers)
