import pyodbc
from static_loader_config import connection_string
from NTA_static_loader import load,route_mapping
def clearTables():
    conn = pyodbc.connect(connection_string)
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


