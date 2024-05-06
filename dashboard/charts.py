import plotly.graph_objects as go
import plotly.express as px

def gauge_chart(title,main_value,ref_value,max_value):
    return go.Figure(go.Indicator(
            domain = {'x': [0, 1], 'y': [0, 1]},
            value = main_value,
            number={'suffix':" sec"},
            mode = "gauge+number+delta",
            title = {'text': title},
            delta = {'reference': ref_value, 'increasing': {'color': "red"}, 'decreasing': {'color': "green"}},
            gauge = {'axis': {'range': [None, max_value]},
                    'steps' : [
                        {'range': [0, main_value-10], 'color': "lightgray"},
                        {'range': [main_value-10, main_value+10], 'color': "gray"}],
                    'threshold' : {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': max_value}}))
def bar_chart(title_of_chart,df,x_name,y_name,x_display_name,y_display_name):
    fig =  px.bar(df, x=x_name, y=y_name, title=title_of_chart)
    fig.update_layout(
        xaxis_title=x_display_name,
        yaxis_title=y_display_name
    )
    return fig
def day_in_week_chart(title_of_chart,df,x_name,y_name,x_display_name,y_display_name,colors):
    fig =  go.Figure(data=[go.Bar(
        x=df.x,y=df.y,marker_color=colors
    )])
    fig.update_layout(
        xaxis_title=x_display_name,
        yaxis_title=y_display_name,
        title_text=title_of_chart
    )
    return fig
def line_chart(title_of_chart,df,x_name,y_name,x_display_name,y_display_name):
    fig =  px.line(df, x=x_name, y=y_name, title=title_of_chart)
    fig.update_layout(
        xaxis_title=x_display_name,
        yaxis_title=y_display_name
    )
    return fig