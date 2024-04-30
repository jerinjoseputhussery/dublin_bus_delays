from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
from config import connection_string
import pandas as pd
import pyodbc
import datetime
import plotly.graph_objects as go



app = Dash(__name__)



# Define the layout of the app
app.layout = html.Div(children=[
    dcc.Interval(id='refresh', interval=60000),
    html.H1(children='Dublin Bus Delay Dashboard'),
    dcc.Dropdown(['Today','All-time'], 'Today', id='dropdown-selection'),
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
@app.callback(Output('timeline', 'figure'),              
              Output('graph1', 'figure'),
              Output('graph2', 'figure'), 
              Output('last_update_time', 'children'),             
              [Input('dropdown-selection', 'value'),
               Input('interval-component', 'n_intervals')])

def update_refresh(value,n):
    conn = pyodbc.connect(connection_string)
    cursor = conn.cursor()    
    # Query the database
    
    cursor.execute('SELECT AVG(current_delay) FROM delays')
    avg_delay =  cursor.fetchone()[0]
    cursor.execute('select AVG(current_delay) from delays where entry_id < (SELECT MAX(entry_id) FROM delays)')
    prev_avg_delay =  cursor.fetchone()[0]
    cursor.execute('SELECT MAX(current_delay) FROM delays')
    max_delay =  cursor.fetchone()[0]
    cursor.execute('SELECT TOP 1 * FROM delays order by entry_id desc')
    last_row = cursor.fetchone()
    curr_delay =  last_row[2]
    last_fetch_time = last_row[1]
    cursor.execute('select TOP 1 current_delay from delays where entry_id < (SELECT MAX(entry_id) FROM delays) order by entry_id desc')
    prev_delay = cursor.fetchone()[0]
    fig1=go.Figure(go.Indicator(
            domain = {'x': [0, 1], 'y': [0, 1]},
            value = avg_delay,
            number={'suffix':" sec"},
            mode = "gauge+number+delta",
            title = {'text': "Average Delay"},
            delta = {'reference': prev_avg_delay, 'increasing': {'color': "red"}, 'decreasing': {'color': "green"}},
            gauge = {'axis': {'range': [None, max_delay]},
                    'steps' : [
                        {'range': [0, avg_delay-10], 'color': "lightgray"},
                        {'range': [avg_delay-10, avg_delay+10], 'color': "gray"}],
                    'threshold' : {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': max_delay}}))
    fig2=go.Figure(go.Indicator(
            domain = {'x': [0, 1], 'y': [0, 1]},
            value = curr_delay,
            number={'suffix':" sec"},
            mode = "gauge+number+delta",
            title = {'text': "Current Delay"},
            delta = {'reference': prev_delay, 'increasing': {'color': "red"}, 'decreasing': {'color': "green"}},
            gauge = {'axis': {'range': [None, max_delay]},
                    'steps' : [
                        {'range': [0, curr_delay-10], 'color': "lightgray"},
                        {'range': [curr_delay-10, curr_delay+10], 'color': "gray"}],
                    'threshold' : {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': max_delay}}))
      
    
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
    return fig0,fig1,fig2,html.P('Last updated ' +str(datetime.datetime.now()))
if __name__ == '__main__':
    app.run(debug=True)
