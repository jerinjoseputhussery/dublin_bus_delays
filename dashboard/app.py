from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
from config import connection_string
import pandas as pd
import pyodbc
import dash_bootstrap_components as dbc
import datetime,pytz
import plotly.graph_objects as go
from charts import gauge_chart,bar_chart,line_chart,day_in_week_chart
from methods import giveMeRoutes,giveMeRouteName,giveMeDFs,giveMe4DFs,giveAllRouteIds,top10routes,getColors4Weather,getColors4Day,getVectorSrc,getCurrentWeather,getColors4Times
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
   
    html.Div(className='line-charts',children=[
        dcc.Graph(id='timeline',style={'width':'80%','height':'100%'}),
        html.Div(className='current-weather',children=[
            html.H5(children='Current Dublin Weather'),
            html.Img(id='img1',alt='weather vector',title='Current Dublin Weather',style={
               'transform':'scale(2)',
               'display': 'block',
                'margin-left': 'auto',
                'margin-right': 'auto',
               'padding-top':'5%'

            }),
            html.H5(id='weather_code_desc_id',style={'text-align':'center','padding-top':'7%'}),
            html.H2(id='current_temp_id',style={'text-align':'center'}),
            html.H6(children='Temperature/ Feels-like',style={'text-align':'center'})

        ])
    ]),
    
    html.Div(className='gauges',children=[
        dcc.Graph(
            id='graph1',
            className='gauge'
                   
        ),
        dcc.Graph(
            id='graph2',
            className='gauge'
            
        ),
        html.Div(className='table-chart',children=[
            html.H4(id='top-heading', children='Top delayed routes'),
            dash_table.DataTable(
                id='table-graph',  
                style_cell={'textAlign': 'left','font-family':'Helvetica'},
            ),            
        ])
        
    ]),
    html.Div(className='bar-charts',children=[
        dcc.Graph(id='bar-chart1',style={'width':'70%','height':'100%'}),
        dcc.Graph(id='pie-chart1',style={'width':'30%','margin-right':'2%'}), 
    ]),  
    html.Div(className='weather-div',children=[
        dcc.Graph(id='bar-chart2',style={'width':'60%','height':'100%'}),
        # dcc.Graph(id='pie-chart1',style={'width':'60%','height':'75%'}), 
         dcc.Graph(id='bar-chart3',style={'width':'40%'}),        
        
    ]),   
    html.Div(id='last_update_time',
             style={'font-size': '10px','margin-left':'10px'}),
    dcc.Interval(
            id='interval-component',
            interval=15*60*1000, # in milliseconds
            n_intervals=0
    )    

])])
@app.callback(
    Output('direction-selection', 'options'),
    Output('direction-selection', 'disabled'),
    Output('direction-selection', 'value'),
    Input('route-selection', 'value'))
def set_direction(route_short_name):
    # disabling dropdown if the selection is all-routes
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
              Output('top-heading', 'children'),
              Output('table-graph', 'data'), 
              Output('timeline', 'figure'),
              Output('bar-chart1', 'figure'),
              Output('bar-chart2', 'figure'),
               Output('pie-chart1', 'figure'),
               Output('img1', 'src'),
               Output('weather_code_desc_id', 'children'), 
               Output('current_temp_id', 'children'), 
               Output('bar-chart3', 'figure'),
              Output('last_update_time', 'children'),             
              [Input('route-selection', 'value'),
               Input('direction-selection', 'value'),
                Input('dropdown-selection', 'value'),               
               Input('interval-component', 'n_intervals')])

def update_refresh(route_short_name,direction_title,value,n):    
    conn = pyodbc.connect(connection_string)
    cursor = conn.cursor()
    current_weather=getCurrentWeather()
    src= getVectorSrc(current_weather)
    weather_code_desc=current_weather[1]
    current_temp=current_weather[3]
    apparent_temp=current_weather[4]
    # Query the database
    if(value=='Today'):
        topHeading = 'Today\'s Top delayed routes'
        table_data = top10routes('Today')
        # table_title = 'Top 10 delayed routes Today'
        #Pie chart
        cursor.execute('select wc.code_description,COUNT(w.weather_code) from weather w INNER JOIN weather_codes wc on w.weather_code=wc.code where CONVERT(date, w.entry_timestamp)=CONVERT(date, GETDATE()) GROUP BY w.weather_code,wc.code_description')    
        pie1 = px.pie(giveMeDFs(cursor.fetchall()), values='y', names='x') 
        pie1.update_layout(
            title='Dublin Weather Today'
        )  
    else:
        topHeading = 'All-time Top delayed routes'
        table_data = top10routes('All-time')
        # table_title = 'Top 10 delayed routesAll-time'
        #Pie chart
        cursor.execute('select code_description,code_count from weather_codes where code_count>0')    
        pie1 = px.pie(giveMeDFs(cursor.fetchall()), values='y', names='x') 
        pie1.update_layout(
            title='All-time Dublin Weather'
        )  


    
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
            fig0=line_chart('Today\'s Delay from all '+ str(len(routes_dict))+' bus routes',giveMe4DFs(cursor.fetchall()),'x','y','Time/Date','Parameters')
            
            #Weather conditions bar
            cursor.execute('SELECT wc.code_description, AVG(d.current_delay) as avg_delay FROM weather w INNER JOIN delays d ON w.entry_id = d.entry_id INNER JOIN weather_codes wc ON w.weather_code = wc.code WHERE CONVERT(date, d.entry_timestamp)=CONVERT(date, GETDATE()) GROUP BY w.weather_code, wc.code_description;')
            df = giveMeDFs(cursor.fetchall())    
            bar1=day_in_week_chart('Today\'s Delay with Weather conditions from All-routes',df,'x','y','Weather conditions','Average Delays',getColors4Weather(df))
        
            # Times of the day bar
            cursor.execute('WITH DelayAverages AS ( SELECT CASE WHEN DATEPART(HOUR, entry_timestamp) BETWEEN 5 AND 11 THEN \'Morning\' WHEN DATEPART(HOUR, entry_timestamp) BETWEEN 12 AND 16 THEN \'Afternoon\' WHEN DATEPART(HOUR, entry_timestamp) BETWEEN 17 AND 20 THEN \'Evening\' WHEN DATEPART(HOUR, entry_timestamp) BETWEEN 21 AND 23 THEN \'Night\' ELSE \'Midnight\' END AS time_of_day, AVG(current_delay) AS average_delay'+
                           ' FROM delays WHERE CONVERT(date, entry_timestamp)=CONVERT(date, GETDATE()) GROUP BY CASE WHEN DATEPART(HOUR, entry_timestamp) BETWEEN 5 AND 11 THEN \'Morning\' WHEN DATEPART(HOUR, entry_timestamp) BETWEEN 12 AND 16 THEN \'Afternoon\' WHEN DATEPART(HOUR, entry_timestamp) BETWEEN 17 AND 20 THEN \'Evening\' WHEN DATEPART(HOUR, entry_timestamp) BETWEEN 21 AND 23 THEN \'Night\' ELSE \'Midnight\' END ) SELECT time_of_day, average_delay FROM DelayAverages ORDER BY CASE WHEN time_of_day = \'Midnight\' THEN 1 WHEN time_of_day = \'Morning\' THEN 2 WHEN time_of_day = \'Afternoon\' THEN 3 WHEN time_of_day = \'Evening\' THEN 4 WHEN time_of_day = \'Night\' THEN 5 END;')
            df = giveMeDFs(cursor.fetchall())    
            bar3=day_in_week_chart('Today\'s Delay at various times of the Day',df,'x','y','Times of the Day','Average Delays',getColors4Times(df))
        
        else:
            cursor.execute('select CONVERT(date, d.entry_timestamp),AVG(d.current_delay),AVG(w.temperature_2m),AVG(w.wind_speed_10m) from delays d INNER JOIN weather w on w.entry_id=d.entry_id group by CONVERT(date, d.entry_timestamp)  order by CONVERT(date, d.entry_timestamp)')       
            fig0=line_chart('All Time Delay from all '+ str(len(routes_dict))+' bus routes',giveMe4DFs(cursor.fetchall()),'x','y','Time/Date','Parameters')
            
            #Weather conditions bar
            cursor.execute('SELECT wc.code_description, AVG(d.current_delay) as avg_delay FROM weather w INNER JOIN delays d ON w.entry_id = d.entry_id INNER JOIN weather_codes wc ON w.weather_code = wc.code GROUP BY w.weather_code, wc.code_description;')
            df = giveMeDFs(cursor.fetchall())    
            bar1=day_in_week_chart('All-time Delay with Weather conditions from All-routes',df,'x','y','Weather conditions','Average Delays',getColors4Weather(df))
            
            # Times of the day bar
            cursor.execute('WITH DelayAverages AS ( SELECT CASE WHEN DATEPART(HOUR, entry_timestamp) BETWEEN 5 AND 11 THEN \'Morning\' WHEN DATEPART(HOUR, entry_timestamp) BETWEEN 12 AND 16 THEN \'Afternoon\' WHEN DATEPART(HOUR, entry_timestamp) BETWEEN 17 AND 20 THEN \'Evening\' WHEN DATEPART(HOUR, entry_timestamp) BETWEEN 21 AND 23 THEN \'Night\' ELSE \'Midnight\' END AS time_of_day, AVG(current_delay) AS average_delay'+
                           ' FROM delays GROUP BY CASE WHEN DATEPART(HOUR, entry_timestamp) BETWEEN 5 AND 11 THEN \'Morning\' WHEN DATEPART(HOUR, entry_timestamp) BETWEEN 12 AND 16 THEN \'Afternoon\' WHEN DATEPART(HOUR, entry_timestamp) BETWEEN 17 AND 20 THEN \'Evening\' WHEN DATEPART(HOUR, entry_timestamp) BETWEEN 21 AND 23 THEN \'Night\' ELSE \'Midnight\' END ) SELECT time_of_day, average_delay FROM DelayAverages ORDER BY CASE WHEN time_of_day = \'Midnight\' THEN 1 WHEN time_of_day = \'Morning\' THEN 2 WHEN time_of_day = \'Afternoon\' THEN 3 WHEN time_of_day = \'Evening\' THEN 4 WHEN time_of_day = \'Night\' THEN 5 END;')
            df = giveMeDFs(cursor.fetchall())    
            bar3=day_in_week_chart('All-time Delay at various times of the Day',df,'x','y','Times of the Day','Average Delays',getColors4Times(df))

        # Day in week bar
        cursor.execute('SELECT DATENAME(WEEKDAY, entry_timestamp) AS day_of_week, AVG(current_delay) AS avg_delay FROM delays GROUP BY DATENAME(WEEKDAY, entry_timestamp) ORDER BY CASE WHEN DATENAME(WEEKDAY, entry_timestamp) = \'Sunday\' THEN 7 WHEN DATENAME(WEEKDAY, entry_timestamp) = \'Monday\' THEN 1 WHEN DATENAME(WEEKDAY, entry_timestamp) = \'Tuesday\' THEN 2 WHEN DATENAME(WEEKDAY, entry_timestamp) = \'Wednesday\' THEN 3 WHEN DATENAME(WEEKDAY, entry_timestamp) = \'Thursday\' THEN 4 WHEN DATENAME(WEEKDAY, entry_timestamp) = \'Friday\' THEN 5 ELSE 6 END;')
        df = giveMeDFs(cursor.fetchall())      
        bar2=day_in_week_chart('Average Delay with Day of Weeks from All routes',df,'x','y','Day of week','Average Delays',getColors4Day(df))    
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
                fig0=line_chart('Today\'s Delay in '+route_short_name,giveMe4DFs(cursor.fetchall()),'x','y','Time/Date','Parameters')
                
                #Weather conditions bar
                cursor.execute('SELECT wc.code_description, AVG(rd.current_delay) as avg_delay FROM weather w INNER JOIN route_delays rd ON w.entry_id = rd.entry_id INNER JOIN weather_codes wc ON w.weather_code = wc.code WHERE CONVERT(date, rd.entry_timestamp)=CONVERT(date, GETDATE()) AND rd.route_id=? GROUP BY w.weather_code, wc.code_description',routes_dict[route_short_name])
                df = giveMeDFs(cursor.fetchall())    
                bar1=day_in_week_chart('Today\'s Delay with Weather conditions from '+route_short_name,df,'x','y','Weather conditions','Average Delays',getColors4Weather(df))

                # Times of the day bar
                cursor.execute('WITH DelayAverages AS ( SELECT CASE WHEN DATEPART(HOUR, entry_timestamp) BETWEEN 5 AND 11 THEN \'Morning\' WHEN DATEPART(HOUR, entry_timestamp) BETWEEN 12 AND 16 THEN \'Afternoon\' WHEN DATEPART(HOUR, entry_timestamp) BETWEEN 17 AND 20 THEN \'Evening\' WHEN DATEPART(HOUR, entry_timestamp) BETWEEN 21 AND 23 THEN \'Night\' ELSE \'Midnight\' END AS time_of_day, AVG(current_delay) AS average_delay'+
                            ' FROM route_delays WHERE CONVERT(date, entry_timestamp)=CONVERT(date, GETDATE()) AND route_id=? GROUP BY CASE WHEN DATEPART(HOUR, entry_timestamp) BETWEEN 5 AND 11 THEN \'Morning\' WHEN DATEPART(HOUR, entry_timestamp) BETWEEN 12 AND 16 THEN \'Afternoon\' WHEN DATEPART(HOUR, entry_timestamp) BETWEEN 17 AND 20 THEN \'Evening\' WHEN DATEPART(HOUR, entry_timestamp) BETWEEN 21 AND 23 THEN \'Night\' ELSE \'Midnight\' END ) SELECT time_of_day, average_delay FROM DelayAverages ORDER BY CASE WHEN time_of_day = \'Midnight\' THEN 1 WHEN time_of_day = \'Morning\' THEN 2 WHEN time_of_day = \'Afternoon\' THEN 3 WHEN time_of_day = \'Evening\' THEN 4 WHEN time_of_day = \'Night\' THEN 5 END;',routes_dict[route_short_name])
                df = giveMeDFs(cursor.fetchall())    
                bar3=day_in_week_chart('Today\'s Delay at various times of the Day (Route '+route_short_name+')',df,'x','y','Times of the Day','Average Delays',getColors4Times(df))
            else:
                cursor.execute('select CONVERT(date, d.entry_timestamp),AVG(d.current_delay),AVG(w.temperature_2m),AVG(w.wind_speed_10m) from route_delays d INNER JOIN weather w on w.entry_id=d.entry_id '+
                              'where route_id in (select route_id from route_mapping where route_short_name=?) group by CONVERT(date, d.entry_timestamp)  order by CONVERT(date, d.entry_timestamp)',route_short_name)       
                fig0=line_chart('All Time Delay in '+route_short_name,giveMe4DFs(cursor.fetchall()),'x','y','Time/Date','Parameters')
                
                #Weather conditions bar
                cursor.execute('SELECT wc.code_description, AVG(rd.current_delay) as avg_delay FROM weather w INNER JOIN route_delays rd ON w.entry_id = rd.entry_id INNER JOIN weather_codes wc ON w.weather_code = wc.code WHERE rd.route_id=? GROUP BY w.weather_code, wc.code_description',routes_dict[route_short_name])
                df = giveMeDFs(cursor.fetchall())    
                bar1=day_in_week_chart('All-time Delay with Weather conditions from '+route_short_name,df,'x','y','Weather conditions','Average Delays',getColors4Weather(df))
                
                # Times of the day bar
                cursor.execute('WITH DelayAverages AS ( SELECT CASE WHEN DATEPART(HOUR, entry_timestamp) BETWEEN 5 AND 11 THEN \'Morning\' WHEN DATEPART(HOUR, entry_timestamp) BETWEEN 12 AND 16 THEN \'Afternoon\' WHEN DATEPART(HOUR, entry_timestamp) BETWEEN 17 AND 20 THEN \'Evening\' WHEN DATEPART(HOUR, entry_timestamp) BETWEEN 21 AND 23 THEN \'Night\' ELSE \'Midnight\' END AS time_of_day, AVG(current_delay) AS average_delay'+
                            ' FROM route_delays WHERE route_id=? GROUP BY CASE WHEN DATEPART(HOUR, entry_timestamp) BETWEEN 5 AND 11 THEN \'Morning\' WHEN DATEPART(HOUR, entry_timestamp) BETWEEN 12 AND 16 THEN \'Afternoon\' WHEN DATEPART(HOUR, entry_timestamp) BETWEEN 17 AND 20 THEN \'Evening\' WHEN DATEPART(HOUR, entry_timestamp) BETWEEN 21 AND 23 THEN \'Night\' ELSE \'Midnight\' END ) SELECT time_of_day, average_delay FROM DelayAverages ORDER BY CASE WHEN time_of_day = \'Midnight\' THEN 1 WHEN time_of_day = \'Morning\' THEN 2 WHEN time_of_day = \'Afternoon\' THEN 3 WHEN time_of_day = \'Evening\' THEN 4 WHEN time_of_day = \'Night\' THEN 5 END;',routes_dict[route_short_name])
                df = giveMeDFs(cursor.fetchall())    
                bar3=day_in_week_chart('All-time Delay at various times of the Day (Route '+route_short_name+')',df,'x','y','Times of the Day','Average Delays',getColors4Times(df))
            # Day in week bar
            cursor.execute('SELECT DATENAME(WEEKDAY, entry_timestamp) AS day_of_week, AVG(current_delay) AS avg_delay FROM route_delays WHERE route_id=? GROUP BY DATENAME(WEEKDAY, entry_timestamp) ORDER BY CASE WHEN DATENAME(WEEKDAY, entry_timestamp) = \'Sunday\' THEN 7 WHEN DATENAME(WEEKDAY, entry_timestamp) = \'Monday\' THEN 1 WHEN DATENAME(WEEKDAY, entry_timestamp) = \'Tuesday\' THEN 2 WHEN DATENAME(WEEKDAY, entry_timestamp) = \'Wednesday\' THEN 3 WHEN DATENAME(WEEKDAY, entry_timestamp) = \'Thursday\' THEN 4 WHEN DATENAME(WEEKDAY, entry_timestamp) = \'Friday\' THEN 5 ELSE 6 END;',routes_dict[route_short_name])
            df = giveMeDFs(cursor.fetchall())      
            bar2=day_in_week_chart('Average Delay with Day of Weeks from '+route_short_name,df,'x','y','Day of week','Average Delays',getColors4Day(df))
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

                #Weather conditions bar
                cursor.execute('SELECT wc.code_description, AVG(rd.current_delay) as avg_delay FROM weather w INNER JOIN route_delays rd ON w.entry_id = rd.entry_id INNER JOIN weather_codes wc ON w.weather_code = wc.code WHERE CONVERT(date, rd.entry_timestamp)=CONVERT(date, GETDATE()) AND rd.route_id=? AND rd.direction_id=? GROUP BY w.weather_code, wc.code_description',routes_dict[route_short_name],direction[0])
                df = giveMeDFs(cursor.fetchall())    
                bar1=day_in_week_chart('Today\'s Delay with Weather conditions from '+route_short_name+' in '+direction_title,df,'x','y','Weather conditions','Average Delays',getColors4Weather(df))
                
                # Times of the day bar
                cursor.execute('WITH DelayAverages AS ( SELECT CASE WHEN DATEPART(HOUR, entry_timestamp) BETWEEN 5 AND 11 THEN \'Morning\' WHEN DATEPART(HOUR, entry_timestamp) BETWEEN 12 AND 16 THEN \'Afternoon\' WHEN DATEPART(HOUR, entry_timestamp) BETWEEN 17 AND 20 THEN \'Evening\' WHEN DATEPART(HOUR, entry_timestamp) BETWEEN 21 AND 23 THEN \'Night\' ELSE \'Midnight\' END AS time_of_day, AVG(current_delay) AS average_delay'+
                            ' FROM route_delays WHERE CONVERT(date, entry_timestamp)=CONVERT(date, GETDATE()) AND route_id=? AND direction_id=? GROUP BY CASE WHEN DATEPART(HOUR, entry_timestamp) BETWEEN 5 AND 11 THEN \'Morning\' WHEN DATEPART(HOUR, entry_timestamp) BETWEEN 12 AND 16 THEN \'Afternoon\' WHEN DATEPART(HOUR, entry_timestamp) BETWEEN 17 AND 20 THEN \'Evening\' WHEN DATEPART(HOUR, entry_timestamp) BETWEEN 21 AND 23 THEN \'Night\' ELSE \'Midnight\' END ) SELECT time_of_day, average_delay FROM DelayAverages ORDER BY CASE WHEN time_of_day = \'Midnight\' THEN 1 WHEN time_of_day = \'Morning\' THEN 2 WHEN time_of_day = \'Afternoon\' THEN 3 WHEN time_of_day = \'Evening\' THEN 4 WHEN time_of_day = \'Night\' THEN 5 END;',routes_dict[route_short_name],direction[0])
                df = giveMeDFs(cursor.fetchall())    
                bar3=day_in_week_chart('Today\'s Delay at various times of the Day (Route '+route_short_name+')',df,'x','y','Times of the Day','Average Delays',getColors4Times(df))
                
            else:
                cursor.execute('select CONVERT(date, d.entry_timestamp),AVG(d.current_delay),AVG(w.temperature_2m),AVG(w.wind_speed_10m) from route_delays d INNER JOIN weather w on w.entry_id=d.entry_id '+
                              'where route_id in (select route_id from route_mapping where route_short_name=?) AND direction_id=? group by CONVERT(date, d.entry_timestamp)  order by CONVERT(date, d.entry_timestamp)',route_short_name,direction[0])       
                fig0=line_chart('All Time Delay from'+route_short_name+' in '+direction_title,giveMe4DFs(cursor.fetchall()),'x','y','Time/Date','Delay')

                #Weather conditions bar
                cursor.execute('SELECT wc.code_description, AVG(rd.current_delay) as avg_delay FROM weather w INNER JOIN route_delays rd ON w.entry_id = rd.entry_id INNER JOIN weather_codes wc ON w.weather_code = wc.code WHERE rd.route_id=? AND rd.direction_id=? GROUP BY w.weather_code, wc.code_description',routes_dict[route_short_name],direction[0])
                df = giveMeDFs(cursor.fetchall())    
                bar1=day_in_week_chart('All-time Delay with Weather conditions from '+route_short_name+' in '+direction_title,df,'x','y','Weather conditions','Average Delays',getColors4Weather(df))
                
                # Times of the day bar
                cursor.execute('WITH DelayAverages AS ( SELECT CASE WHEN DATEPART(HOUR, entry_timestamp) BETWEEN 5 AND 11 THEN \'Morning\' WHEN DATEPART(HOUR, entry_timestamp) BETWEEN 12 AND 16 THEN \'Afternoon\' WHEN DATEPART(HOUR, entry_timestamp) BETWEEN 17 AND 20 THEN \'Evening\' WHEN DATEPART(HOUR, entry_timestamp) BETWEEN 21 AND 23 THEN \'Night\' ELSE \'Midnight\' END AS time_of_day, AVG(current_delay) AS average_delay'+
                            ' FROM route_delays WHERE route_id=? AND direction_id=? GROUP BY CASE WHEN DATEPART(HOUR, entry_timestamp) BETWEEN 5 AND 11 THEN \'Morning\' WHEN DATEPART(HOUR, entry_timestamp) BETWEEN 12 AND 16 THEN \'Afternoon\' WHEN DATEPART(HOUR, entry_timestamp) BETWEEN 17 AND 20 THEN \'Evening\' WHEN DATEPART(HOUR, entry_timestamp) BETWEEN 21 AND 23 THEN \'Night\' ELSE \'Midnight\' END ) SELECT time_of_day, average_delay FROM DelayAverages ORDER BY CASE WHEN time_of_day = \'Midnight\' THEN 1 WHEN time_of_day = \'Morning\' THEN 2 WHEN time_of_day = \'Afternoon\' THEN 3 WHEN time_of_day = \'Evening\' THEN 4 WHEN time_of_day = \'Night\' THEN 5 END;',routes_dict[route_short_name],direction[0])
                df = giveMeDFs(cursor.fetchall())    
                bar3=day_in_week_chart('All-time Delay at various times of the Day (Route '+route_short_name+')',df,'x','y','Times of the Day','Average Delays',getColors4Times(df))
            # Day in week bar
            cursor.execute('SELECT DATENAME(WEEKDAY, entry_timestamp) AS day_of_week, AVG(current_delay) AS avg_delay FROM route_delays WHERE route_id=? and direction_id=? GROUP BY DATENAME(WEEKDAY, entry_timestamp) ORDER BY CASE WHEN DATENAME(WEEKDAY, entry_timestamp) = \'Sunday\' THEN 7 WHEN DATENAME(WEEKDAY, entry_timestamp) = \'Monday\' THEN 1 WHEN DATENAME(WEEKDAY, entry_timestamp) = \'Tuesday\' THEN 2 WHEN DATENAME(WEEKDAY, entry_timestamp) = \'Wednesday\' THEN 3 WHEN DATENAME(WEEKDAY, entry_timestamp) = \'Thursday\' THEN 4 WHEN DATENAME(WEEKDAY, entry_timestamp) = \'Friday\' THEN 5 ELSE 6 END;',routes_dict[route_short_name],direction[0])
            df = giveMeDFs(cursor.fetchall())      
            bar2=day_in_week_chart('Average Delay with Day of Weeks from '+route_short_name+' in '+direction_title,df,'x','y','Day of week','Average Delays',getColors4Day(df))

    
    
    
    # #map
    # cursor.execute('select CONVERT(FLOAT,shape_pt_lat),CONVERT(FLOAT,shape_pt_lon) from shapes where shape_id in (select max(shape_id) from trips where route_id in (select route_id from route_mapping where is_active=1 and route_short_name=?)) order by shape_pt_sequence','27')
    # df = giveMeDFs(cursor.fetchall())
    # map0 = go.Figure(go.Scattermapbox(
    # mode = "markers+lines",
    # lon = df['x'],
    # lat = df['y'],
    # marker = {'size': 10}))
    # print(datetime.datetime.now())
    cursor.close()
    conn.close()
    return fig1,fig2,topHeading,table_data,fig0,bar1,bar2,pie1,src,weather_code_desc,str(current_temp)+'°/ '+str(apparent_temp)+'°C',bar3,html.P('Last updated ' +str(datetime.datetime.now(pytz.timezone("Europe/Dublin"))))
if __name__ == '__main__':
    app.run(debug=True)
