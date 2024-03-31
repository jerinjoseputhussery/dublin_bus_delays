import pyodbc
import os
import csv
from static_loader_config import database,file_path,password,server,username


conn = pyodbc.connect('DRIVER={SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+password)

cursor = conn.cursor()

table_name = os.path.splitext(os.path.basename(file_path))[0] 
with open(file_path, 'r',encoding="utf8") as file:    
    # next(file)    
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
        print(count)
        print(list(data.values()))
        # print(sql_query)       
        cursor.execute(sql_query, list(data.values()))
        count+=1            
        
    print(count ,' rows got written')
    print('1 Table got written')

conn.commit()
cursor.close()
conn.close()
