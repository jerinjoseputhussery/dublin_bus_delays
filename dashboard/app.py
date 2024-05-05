from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
from config import connection_string
import pandas as pd
import pyodbc
import datetime
import plotly.graph_objects as go
from charts import gauge_chart
from methods import giveMeRoutes,giveMeRouteName

app = Dash(__name__)
routes_dict = giveMeRoutes()
routes = list(routes_dict.keys())
routes.insert(0, 'All-routes')


# Define the layout of the app
app.layout = html.Div(children=[
    dcc.Interval(id='refresh', interval=60000),
    html.H1(children='Dublin Bus Delay Dashboard'),   
    dcc.Dropdown(routes, 'All-routes', id='route-selection',style={'width':'35%','display':'inline-block'}), 
    dcc.Dropdown(id='direction-selection',style={'width':'35%','display':'inline-block'}), 
    dcc.Dropdown(['Today','All-time'], 'Today', id='dropdown-selection',
                 style={'width':'35%','display':'inline-block'}),
    dcc.Graph(id='timeline'),
    dcc.Graph(
        id='graph1',
        style={'display':'inline-block','width': '90vh', 'height': '90vh'},        
    ),
    dcc.Graph(
        id='graph2',
        style={'display':'inline-block','width': '90vh', 'height': '90vh'},        
    ),
    html.Div(id='last_update_time',
             style={'font-size': '10px'}),
    dcc.Interval(
            id='interval-component',
            interval=5*60*1000, # in milliseconds
            n_intervals=0
    )

])
@app.callback(
    Output('direction-selection', 'options'),
    Input('route-selection', 'value'))
def set_direction(route_short_name):
    # ivde all routes aanenkil ee drop down diable cheyyanam
    route_name = giveMeRouteName(route_short_name)
    
    routes_dir = list(route_name.values())
    return routes_dir

@app.callback(             
              Output('graph1', 'figure'),
              Output('graph2', 'figure'), 
              Output('timeline', 'figure'),
              Output('last_update_time', 'children'),             
              [Input('route-selection', 'value'),
                Input('dropdown-selection', 'value'),               
               Input('interval-component', 'n_intervals')])

def update_refresh(route_short_name,value,n):
    conn = pyodbc.connect(connection_string)
    cursor = conn.cursor()    
    # Query the database
    
    if(route_short_name=='All-routes'):
        cursor.execute('SELECT AVG(current_delay) FROM delays')
        avg_delay =  cursor.fetchone()[0]
        cursor.execute('select AVG(current_delay) from delays where entry_id < (SELECT MAX(entry_id) FROM delays)')
        prev_avg_delay =  cursor.fetchone()[0]
        cursor.execute('SELECT MAX(current_delay) FROM delays')
        max_delay =  cursor.fetchone()[0]
        cursor.execute('SELECT TOP 1 * FROM delays order by entry_id desc')
        curr_delay = cursor.fetchone()[2]        
        cursor.execute('select TOP 1 current_delay from delays where entry_id < (SELECT MAX(entry_id) FROM delays) order by entry_id desc')
        prev_delay = cursor.fetchone()[0]
    else:
        cursor.execute('SELECT AVG(current_delay) FROM route_delays where route_id=?',routes_dict[route_short_name])
        avg_delay =  cursor.fetchone()[0]
        cursor.execute('select AVG(current_delay) from route_delays where entry_id < (SELECT MAX(entry_id) FROM route_delays where route_id=?) and route_id=?',[routes_dict[route_short_name],routes_dict[route_short_name]])
        prev_avg_delay =  cursor.fetchone()[0]
        cursor.execute('SELECT MAX(current_delay) FROM route_delays where route_id=?',routes_dict[route_short_name])
        max_delay =  cursor.fetchone()[0]
        cursor.execute('SELECT TOP 1 current_delay FROM route_delays where route_id=? order by entry_id desc',routes_dict[route_short_name])
        curr_delay = cursor.fetchone()[0]        
        cursor.execute('select TOP 1 current_delay from route_delays where entry_id < (SELECT MAX(entry_id) FROM route_delays where route_id=?) and route_id=? order by entry_id desc',[routes_dict[route_short_name],routes_dict[route_short_name]])
        prev_delay = cursor.fetchone()[0]
        
    # print(routes)
    fig1=gauge_chart('Average Delay',avg_delay,prev_avg_delay,max_delay)    
    fig2=gauge_chart('Current Delay',curr_delay,prev_delay,max_delay)    
      
    
    if(value=='Today'):
        cursor.execute('select entry_timestamp,current_delay from delays where CONVERT(date, entry_timestamp)=CONVERT(date, GETDATE()) order by entry_id')
        today_delay =  cursor.fetchall()   
        entry_timestamp_arr = []
        current_delay_arr = []
        for row in today_delay:
            entry_timestamp_arr.append(row[0])
            current_delay_arr.append(row[1]) 
        df = pd.DataFrame(dict(
            time = entry_timestamp_arr,
            delay = current_delay_arr
        ))  
        fig0 = px.line(df, x='time', y='delay',title='Today\'s Delay')
    else:
        cursor.execute('select CONVERT(date, entry_timestamp),AVG(current_delay) from delays group by CONVERT(date, entry_timestamp)')
        today_delay =  cursor.fetchall()   
        entry_timestamp_arr = []
        current_delay_arr = []
        for row in today_delay:
            entry_timestamp_arr.append(row[0])
            current_delay_arr.append(row[1]) 
        df = pd.DataFrame(dict(
            dates = entry_timestamp_arr,
            delay = current_delay_arr
        ))  
        fig0 = px.line(df, x='dates', y='delay',title='All-time Delay')
    print(datetime.datetime.now())
    cursor.close()
    conn.close()
    return fig1,fig2,fig0,html.P('Last updated ' +str(datetime.datetime.now()))
if __name__ == '__main__':
    app.run(debug=True)
