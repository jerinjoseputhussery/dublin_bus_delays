import pyodbc
import os
from static_loader_config import database,file_path,password,server,username


conn = pyodbc.connect('DRIVER={SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+password)

cursor = conn.cursor()

table_name = os.path.splitext(os.path.basename(file_path))[0] 
with open(file_path, 'r') as file:    
    next(file)
    lines = file.readlines()    
    for line in lines:        
        data = line.strip().split(',')         
        sql_query = f"INSERT INTO {table_name} VALUES ("
        for i in data:
            sql_query+='?,'
        sql_query = sql_query.rstrip(sql_query[-1])
        sql_query+=')'        
        cursor.execute(sql_query, data)
        print('1 Table got written')

conn.commit()
cursor.close()
conn.close()
