import plotly.graph_objects as go
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
    