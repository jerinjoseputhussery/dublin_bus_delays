import pyodbc
from static_loader_config import database,password,server,username 
from NTA_static_loader import load,route_mapping
def clearTables():
    conn = pyodbc.connect('DRIVER={SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+password)
    cursor = conn.cursor()
    static_tables=['agency','calendar','calendar_dates','feed_info','routes','shapes','stops','trips','stop_times']
    static_tables.reverse()
    for table_name in static_tables:
        statement = 'DELETE FROM '+table_name
        cursor.execute(statement)
    conn.commit()
    cursor.close()
    conn.close() 
    print('All tables got cleared')
def refresh():
    clearTables()
    load()
    route_mapping()
# if __name__ == "__main__":
#     execute()


