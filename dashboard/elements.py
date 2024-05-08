from dash import  html
import dash_bootstrap_components as dbc

def radio(id_value):
    button_group = html.Div(
        [
            dbc.RadioItems(
                id=id_value,
                className="btn-group",
                inputClassName="btn-check",
                labelClassName="btn btn-outline-secondary",
                labelCheckedClassName="active",
                options=[
                    {"label": "Today","value":"Today"},
                    {"label": "All-time","value":"All-time"},
                ],
                value="Today"
            ),
            html.Div(id="radio-div"),
        ],
        className="radio-group",
    )
    return button_group