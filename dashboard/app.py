from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
from config import connection_string
import pandas as pd
import pyodbc
import datetime
import plotly.graph_objects as go
from charts import gauge_chart,bar_chart,line_chart,day_in_week_chart
from methods import giveMeRoutes,giveMeRouteName,giveMeDFs,giveMe4DFs


external_stylesheets = [
    {
        "href": (
            "https://fonts.googleapis.com/css2?"
            "family=Lato:wght@400;700&display=swap"
        ),
        "rel": "stylesheet",
    },
]
app = Dash(__name__,external_stylesheets=external_stylesheets)
app.title = "Dublin Bus Delay Dashboard"

routes_dict = giveMeRoutes()
routes = list(routes_dict.keys())
routes.insert(0, 'All-routes')


# Define the layout of the app
app.layout = html.Div(children=[
    # dcc.Interval(id='refresh', interval=60000),
    html.Div(children=[
    html.H1(children='Dublin Bus Delay Dashboard',className="header-title"),],className="header"),   
    dcc.Dropdown(routes, 'All-routes', id='route-selection',style={'width':'35%','display':'inline-block'}), 
    dcc.Dropdown(id='direction-selection',style={'width':'35%','display':'inline-block'},disabled=True), 
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
    dcc.Graph(id='bar-chart1'),
    dcc.Graph(id='bar-chart2'),
    dcc.Graph(id='pie-chart1'),
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
    Output('direction-selection', 'disabled'),
    Output('direction-selection', 'value'),
    Input('route-selection', 'value'))
def set_direction(route_short_name):
    # ivde all routes aanenkil ee drop down diable cheyyanam
    disabled=False
    if(route_short_name=='All-routes'):
        disabled=True
    route_name = giveMeRouteName(route_short_name)    
    routes_dir = list(route_name.values())
    routes_dir.insert(0, 'Both-directions')
    return routes_dir,disabled,'Both-directions'

@app.callback(       
              Output('graph1', 'figure'),
              Output('graph2', 'figure'), 
              Output('timeline', 'figure'),
              Output('bar-chart1', 'figure'),
              Output('bar-chart2', 'figure'),
               Output('pie-chart1', 'figure'),
              Output('last_update_time', 'children'),             
              [Input('route-selection', 'value'),
               Input('direction-selection', 'value'),
                Input('dropdown-selection', 'value'),               
               Input('interval-component', 'n_intervals')])

def update_refresh(route_short_name,direction_title,value,n):
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
        if(direction_title=='Both-directions' or direction_title==None):
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
        else: 
            direction = [key for key, value in giveMeRouteName(route_short_name).items() if value == direction_title]
            cursor.execute('SELECT AVG(current_delay) FROM route_delays where route_id=? and direction_id=?',routes_dict[route_short_name],direction[0])
            avg_delay =  cursor.fetchone()[0]
            cursor.execute('select AVG(current_delay) from route_delays where entry_id < (SELECT MAX(entry_id) FROM route_delays where route_id=? and direction_id=?) and route_id=? and direction_id=?',[routes_dict[route_short_name],direction[0],routes_dict[route_short_name],direction[0]])
            prev_avg_delay =  cursor.fetchone()[0]
            cursor.execute('SELECT MAX(current_delay) FROM route_delays where route_id=? and direction_id=?',routes_dict[route_short_name],direction[0])
            max_delay =  cursor.fetchone()[0]
            cursor.execute('SELECT TOP 1 current_delay FROM route_delays where route_id=? and direction_id=? order by entry_id desc',routes_dict[route_short_name],direction[0])
            curr_delay = cursor.fetchone()[0]        
            cursor.execute('select TOP 1 current_delay from route_delays where entry_id < (SELECT MAX(entry_id) FROM route_delays where route_id=? and direction_id=?) and route_id=? and direction_id=? order by entry_id desc',[routes_dict[route_short_name],direction[0],routes_dict[route_short_name],direction[0]])
            prev_delay = cursor.fetchone()[0]
        
    # print(routes)
    fig1=gauge_chart('Average Delay',avg_delay,prev_avg_delay,max_delay)    
    fig2=gauge_chart('Current Delay',curr_delay,prev_delay,max_delay)    
      
    
    if(value=='Today'):
        cursor.execute('select d.entry_timestamp,d.current_delay,w.temperature_2m,w.wind_speed_10m from delays d INNER JOIN weather w on w.entry_id=d.entry_id where CONVERT(date, d.entry_timestamp)=CONVERT(date, GETDATE()) order by d.entry_id')        
        fig0=line_chart('Today\'s Delay',giveMe4DFs(cursor.fetchall()),'x','y','Time/Date','Delay')
    else:
        cursor.execute('select CONVERT(date, d.entry_timestamp),AVG(d.current_delay),AVG(w.temperature_2m),AVG(w.wind_speed_10m) from delays d INNER JOIN weather w on w.entry_id=d.entry_id group by CONVERT(date, d.entry_timestamp)  order by CONVERT(date, d.entry_timestamp)')       
        fig0=line_chart('Today\'s Delay',giveMe4DFs(cursor.fetchall()),'x','y','Time/Date','Delay')
    cursor.execute('SELECT wc.code_description, AVG(d.current_delay) as avg_delay FROM weather w INNER JOIN delays d ON w.entry_id = d.entry_id INNER JOIN weather_codes wc ON w.weather_code = wc.code GROUP BY w.weather_code, wc.code_description;')
    
    bar1=bar_chart('Delay with Weather conditions',giveMeDFs(cursor.fetchall()),'x','y','Weather conditions','Average Delays',)
    cursor.execute('SELECT DATENAME(WEEKDAY, entry_timestamp) AS day_of_week, AVG(current_delay) AS avg_delay FROM delays GROUP BY DATENAME(WEEKDAY, entry_timestamp) ORDER BY CASE WHEN DATENAME(WEEKDAY, entry_timestamp) = \'Sunday\' THEN 7 WHEN DATENAME(WEEKDAY, entry_timestamp) = \'Monday\' THEN 1 WHEN DATENAME(WEEKDAY, entry_timestamp) = \'Tuesday\' THEN 2 WHEN DATENAME(WEEKDAY, entry_timestamp) = \'Wednesday\' THEN 3 WHEN DATENAME(WEEKDAY, entry_timestamp) = \'Thursday\' THEN 4 WHEN DATENAME(WEEKDAY, entry_timestamp) = \'Friday\' THEN 5 ELSE 6 END;')
    # bar2=bar_chart('Delay with Day of Weeks',giveMeDFs(cursor.fetchall()),'x','y','Day of week','Average Delay')
    
    df = giveMeDFs(cursor.fetchall())  
    colors = ['lightslategray',] * 7
    colors[df['y'].idxmax()] = 'crimson'  
    bar2=day_in_week_chart('Delay with Day of Weeks',df,'x','y','Day of week','Average Delay',colors)
    
    
    #Pie chart
    cursor.execute('select code_description,code_count from weather_codes where code_count>0')    
    pie1 = px.pie(giveMeDFs(cursor.fetchall()), values='y', names='x') 
    pie1.update_layout(
        title='Dublin Weather'
    )   
    print(datetime.datetime.now())
    cursor.close()
    conn.close()
    return fig1,fig2,fig0,bar1,bar2,pie1,html.P('Last updated ' +str(datetime.datetime.now()))
if __name__ == '__main__':
    app.run(debug=True)
