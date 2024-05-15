from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
from config import connection_string
import pandas as pd
import pyodbc
import dash_bootstrap_components as dbc
import datetime,pytz
import plotly.graph_objects as go
from charts import gauge_chart,bar_chart,line_chart,day_in_week_chart
from methods import giveMeRoutes,giveMeRouteName,giveMeDFs,giveMe4DFs,giveAllRouteIds,top10routes
from elements import radio
from dash import dash_table

external_stylesheets = [
    {
        "href": (
            "https://fonts.googleapis.com/css2?"
            "family=Lato:wght@400;700&display=swap"
        ),
        "rel": "stylesheet",
    },
]
app = Dash(__name__,external_stylesheets=[dbc.themes.BOOTSTRAP,external_stylesheets])
app.title = "Dublin Bus Delay Dashboard"

routes_dict = giveMeRoutes()
routes = list(routes_dict.keys())
routes.insert(0, 'All-routes')


# Define the layout of the app
app.layout = dcc.Loading(
        id="loading",
        type="default",  # or 'cube', 'circle', 'dot', 'circle-dot'
        fullscreen=True,
        color='#222222',
        children=[
    html.Div(children=[
    # dcc.Interval(id='refresh', interval=60000),
    html.Div(children=[
    html.H1(children='Dublin Bus Delay Dashboard',className="header-title"),],className="header"),  
    html.Div(className='dropdown-container',children=[
        dcc.Dropdown(routes, 'All-routes', id='route-selection',className='dropdown',placeholder='Select route',clearable=False), 
        dcc.Dropdown(id='direction-selection',className='dropdown',disabled=True,clearable=False),         
    ]), 
    # dcc.RadioItems(['Today','All-time'], 'Today', id='dropdown-selection',className='radio-inputs'),
    radio('dropdown-selection'),
   
    
    dcc.Graph(id='timeline'),
    html.Div(className='gauges',children=[
        dcc.Graph(
            id='graph1',
            className='gauge'
                   
        ),
        dcc.Graph(
            id='graph2',
            className='gauge'
            
        ),
        dash_table.DataTable(
            id='table-graph',
        ),
    ]),
    
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

])])
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
              Output('table-graph', 'data'), 
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
    if(value=='Today'):
        table_data = top10routes('Today')
    else:
        table_data = top10routes('All-time')


    
    if(route_short_name=='All-routes'):                
        cursor.execute('SELECT AVG(current_delay) FROM delays')
        avg_delay =  cursor.fetchone()[0]
        # cursor.execute('select AVG(current_delay) from delays where entry_id < (SELECT MAX(entry_id) FROM delays)')
        cursor.execute(' select AVG(current_delay) from delays where CONVERT(date, entry_timestamp)<>CONVERT(date, GETDATE())')
        prev_avg_delay =  cursor.fetchone()[0]
        cursor.execute('SELECT MAX(current_delay) FROM delays')
        max_delay =  cursor.fetchone()[0]
        cursor.execute('SELECT TOP 1 * FROM delays order by entry_id desc')
        curr_delay = cursor.fetchone()[2]        
        cursor.execute('select TOP 1 current_delay from delays where entry_id < (SELECT MAX(entry_id) FROM delays) order by entry_id desc')
        prev_delay = cursor.fetchone()[0]
        fig1=gauge_chart('Average Delay from All-routes',avg_delay,prev_avg_delay,max_delay)    
        fig2=gauge_chart('Current Delay in All-routes',curr_delay,prev_delay,max_delay)    
        #Line grpah for all routes
        if(value=='Today'):
            cursor.execute('select d.entry_timestamp,d.current_delay,w.temperature_2m,w.wind_speed_10m from delays d INNER JOIN weather w on w.entry_id=d.entry_id where CONVERT(date, d.entry_timestamp)=CONVERT(date, GETDATE()) order by d.entry_id')        
            fig0=line_chart('Today\'s Delay from all routes',giveMe4DFs(cursor.fetchall()),'x','y','Time/Date','Delay')
        else:
            cursor.execute('select CONVERT(date, d.entry_timestamp),AVG(d.current_delay),AVG(w.temperature_2m),AVG(w.wind_speed_10m) from delays d INNER JOIN weather w on w.entry_id=d.entry_id group by CONVERT(date, d.entry_timestamp)  order by CONVERT(date, d.entry_timestamp)')       
            fig0=line_chart('All Time Delay from all routes',giveMe4DFs(cursor.fetchall()),'x','y','Time/Date','Delay')

    else:
        if(direction_title=='Both-directions' or direction_title==None):
            cursor.execute('SELECT AVG(current_delay) FROM route_delays where route_id in {}'.format(giveAllRouteIds(route_short_name)))
            avg_delay =  cursor.fetchone()[0]
            cursor.execute('select AVG(current_delay) from route_delays where CONVERT(date, entry_timestamp)<>CONVERT(date, GETDATE()) and route_id in {}'.format(giveAllRouteIds(route_short_name)))
            prev_avg_delay =  cursor.fetchone()[0]
            cursor.execute('SELECT MAX(current_delay) FROM route_delays where route_id in {}'.format(giveAllRouteIds(route_short_name)))
            max_delay =  cursor.fetchone()[0]
            cursor.execute('SELECT TOP 1 current_delay FROM route_delays where route_id=? order by entry_id desc',routes_dict[route_short_name])
            curr_delay = cursor.fetchone()[0]        
            cursor.execute('select TOP 1 current_delay from route_delays where entry_id < (SELECT MAX(entry_id) FROM route_delays where route_id in {}) and route_id in {} order by entry_id desc'
                           .format(giveAllRouteIds(route_short_name),giveAllRouteIds(route_short_name)))
            prev_delay = cursor.fetchone()[0]
            fig1=gauge_chart('All-time Average Delay from '+route_short_name,avg_delay,prev_avg_delay,max_delay)    
            fig2=gauge_chart('Current Delay in '+ route_short_name,curr_delay,prev_delay,max_delay)    
            #Line graph for a route
            if(value=='Today'):
                cursor.execute('select d.entry_timestamp,d.current_delay,w.temperature_2m,w.wind_speed_10m from route_delays d INNER JOIN weather w on w.entry_id=d.entry_id where CONVERT(date, d.entry_timestamp)=CONVERT(date, GETDATE()) AND d.route_id=? order by d.entry_id',routes_dict[route_short_name])        
                fig0=line_chart('Today\'s Delay in '+route_short_name,giveMe4DFs(cursor.fetchall()),'x','y','Time/Date','Delay')

            else:
                cursor.execute('select CONVERT(date, d.entry_timestamp),AVG(d.current_delay),AVG(w.temperature_2m),AVG(w.wind_speed_10m) from route_delays d INNER JOIN weather w on w.entry_id=d.entry_id '+
                              'where route_id in (select route_id from route_mapping where route_short_name=?) group by CONVERT(date, d.entry_timestamp)  order by CONVERT(date, d.entry_timestamp)',route_short_name)       
                fig0=line_chart('All Time Delay in '+route_short_name,giveMe4DFs(cursor.fetchall()),'x','y','Time/Date','Delay')

        else: 
            direction = [key for key, value in giveMeRouteName(route_short_name).items() if value == direction_title]
            cursor.execute('SELECT AVG(current_delay) FROM route_delays where route_id in {} and direction_id=?'.format(giveAllRouteIds(route_short_name)),direction[0])
            avg_delay =  cursor.fetchone()[0]
            cursor.execute('select AVG(current_delay) from route_delays where CONVERT(date, entry_timestamp)<>CONVERT(date, GETDATE()) and route_id in {} and direction_id=?'
                           .format(giveAllRouteIds(route_short_name)),direction[0])
            prev_avg_delay =  cursor.fetchone()[0]
            cursor.execute('SELECT MAX(current_delay) FROM route_delays where route_id in {} and direction_id=?'.format(giveAllRouteIds(route_short_name)),direction[0])
            max_delay =  cursor.fetchone()[0]
            cursor.execute('SELECT TOP 1 current_delay FROM route_delays where route_id=? and direction_id=? order by entry_id desc',routes_dict[route_short_name],direction[0])
            curr_delay = cursor.fetchone()[0]        
            cursor.execute('select TOP 1 current_delay from route_delays where entry_id < (SELECT MAX(entry_id) FROM route_delays where route_id in {} and direction_id=?) and route_id in {} and direction_id=? order by entry_id desc'
                           .format(giveAllRouteIds(route_short_name),giveAllRouteIds(route_short_name)),direction[0],direction[0])
            prev_delay = cursor.fetchone()[0]
            fig1=gauge_chart('All-time Average Delay from '+route_short_name,avg_delay,prev_avg_delay,max_delay)    
            fig2=gauge_chart('Current Delay from '+route_short_name,curr_delay,prev_delay,max_delay)    
            #Line graph for a route with direction
            if(value=='Today'):
                cursor.execute('select d.entry_timestamp,d.current_delay,w.temperature_2m,w.wind_speed_10m from route_delays d INNER JOIN weather w on w.entry_id=d.entry_id '
                               +'where CONVERT(date, d.entry_timestamp)=CONVERT(date, GETDATE()) AND route_id=? AND direction_id=? order by d.entry_id',routes_dict[route_short_name],direction[0])        
                fig0=line_chart('Today\'s Delay from '+route_short_name+' in '+direction_title,giveMe4DFs(cursor.fetchall()),'x','y','Time/Date','Delay')

            else:
                cursor.execute('select CONVERT(date, d.entry_timestamp),AVG(d.current_delay),AVG(w.temperature_2m),AVG(w.wind_speed_10m) from route_delays d INNER JOIN weather w on w.entry_id=d.entry_id '+
                              'where route_id in (select route_id from route_mapping where route_short_name=?) AND direction_id=? group by CONVERT(date, d.entry_timestamp)  order by CONVERT(date, d.entry_timestamp)',route_short_name,direction[0])       
                fig0=line_chart('All Time Delay from'+route_short_name+' in '+direction_title,giveMe4DFs(cursor.fetchall()),'x','y','Time/Date','Delay')

    # print(routes)
    
      
    
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
    
    # #map
    # cursor.execute('select CONVERT(FLOAT,shape_pt_lat),CONVERT(FLOAT,shape_pt_lon) from shapes where shape_id in (select max(shape_id) from trips where route_id in (select route_id from route_mapping where is_active=1 and route_short_name=?)) order by shape_pt_sequence','27')
    # df = giveMeDFs(cursor.fetchall())
    # map0 = go.Figure(go.Scattermapbox(
    # mode = "markers+lines",
    # lon = df['x'],
    # lat = df['y'],
    # marker = {'size': 10}))
    print(datetime.datetime.now())
    cursor.close()
    conn.close()
    return fig1,fig2,table_data,fig0,bar1,bar2,pie1,html.P('Last updated ' +str(datetime.datetime.now(pytz.timezone("Europe/Dublin"))))
if __name__ == '__main__':
    app.run(debug=True)
