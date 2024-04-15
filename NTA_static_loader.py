import pyodbc
import os
import csv
from static_loader_config import database,directory,password,server,username 
def route_mapping():
    conn = pyodbc.connect('DRIVER={SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+password)
    cursor = conn.cursor()
    cursor.execute('SELECT route_id,agency_id,route_short_name,route_long_name FROM [dublin_bus].[dbo].[routes] where agency_id in (select agency_id from agency where agency_name like \'%Dublin Bus%\')')
    rows = cursor.fetchall()
    cursor.execute('SELECT COUNT(*) FROM route_mapping')      
    if cursor.fetchone()[0]==0: 
        for row in rows:
            statement  = 'INSERT into route_mapping values(?,?,?)'
            cursor.execute(statement, (row[0],row[2],1))
    else:
        for row in rows:
            cursor.execute('SELECT COUNT(*) FROM route_mapping where route_id=?',row[0])
            if cursor.fetchone()[0]==0: #if route_id does not exist
                cursor.execute('SELECT COUNT(*) FROM route_mapping where route_short_name=?',row[2])
                if cursor.fetchone()[0]==0: #if route_short_name does not exist
                    #add a new row
                    statement  = 'INSERT into route_mapping values(?,?,?)'
                    cursor.execute(statement, (row[0],row[2],1))
                else: #if route_short_name  exist
                    #update is_active of route_short_name to 0
                    statement  = 'UPDATE route_mapping SET is_active=0 where route_short_name=?'
                    cursor.execute(statement, (row[2]))
                    #insert a new row
                    statement  = 'INSERT INTO route_mapping values(?,?,?)'
                    cursor.execute(statement, (row[0],row[2],1))
            else: #if route_id exist
                #check is_active of route_id: if is_active is not 1, set to 1
                cursor.execute('SELECT is_active FROM route_mapping where route_id=?',row[0])
                if cursor.fetchone()[0]!=1:
                    statement  = 'UPDATE route_mapping SET is_active=1 where route_id=?'
                    cursor.execute(statement, (row[0]))
    conn.commit()
    cursor.close()
    conn.close()    
    print('Route mapping completed')            
def load():
    conn = pyodbc.connect('DRIVER={SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+password)
    static_files=['agency.txt','calendar.txt','calendar_dates.txt','feed_info.txt','routes.txt','shapes.txt','stops.txt','trips.txt','stop_times.txt']
    cursor = conn.cursor()
    for file_path in static_files:
        with open(os.path.join(directory, file_path), 'r',encoding="utf8") as file:    
            # next(file)    
            table_name = os.path.splitext(os.path.basename(file_path))[0] 
            csv_reader = csv.DictReader(file)
            #lines = file.readlines() 
            count=0   
            for data in csv_reader:        
                
                # data = line.strip().split(',')   

                #code checks for the file is stops, then it will escape the comma in stop name
                # if(len(data)!=10 and table_name=='stops'):
                #     #print(data[2]+','+data[3])
                #     data[2]=data[2]+','+data[3] 
                #     del data[3]  
                if(table_name=='stop_times'):
                    # print(data['arrival_time'])
                    if(int(data['arrival_time'].split(':')[0])>23):
                        data['arrival_time']=str(int(data['arrival_time'].split(':')[0])-24)+':'+data['arrival_time'].split(':')[1]+':'+data['arrival_time'].split(':')[2]
                    if(int(data['departure_time'].split(':')[0])>23):
                        data['departure_time']=str(int(data['departure_time'].split(':')[0])-24)+':'+data['departure_time'].split(':')[1]+':'+data['departure_time'].split(':')[2]
                
                sql_query = f"INSERT INTO {table_name} VALUES ("
                for i in data:           
                    sql_query+='?,'
                sql_query = sql_query.rstrip(sql_query[-1])
                sql_query+=')' 
                # print(count)
                # print(list(data.values()))
                # print(sql_query)       
                cursor.execute(sql_query, list(data.values()))
                count+=1            
                
            print(count ,' rows got written on table', table_name)
            # print('1 Table got written')
    conn.commit()
    cursor.close()
    conn.close()
    print('Table load completed')
def execute():
    load()
    route_mapping()
if __name__ == "__main__":
    execute()