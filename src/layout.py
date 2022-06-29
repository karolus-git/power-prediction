from dash import html
from dash import dcc
import dash_daq as daq
import dash_bootstrap_components as dbc
from datetime import date
from datetime import datetime

# Stylesheets
stylesheets = [dbc.themes.LUX,]

# Title and subtitle
title = "Power prediction and analysis in France"
subtitle = "Powered by Dash, Docker and Prophet"

# 
header_title = html.H3(
    title
)

header_subtitle =  html.P(
    subtitle
)

footer =  html.P(
    "Original data downloaded from https://www.opendatasoft.com/fr/",
    id="footer-text",
    style={
        "font-size" : "11px"
    }
)

learn_more_button = html.Button(
    'Learn more', 
    id='learn-more-button', 
    n_clicks=0,
)

train_button = html.Button(
    'Train models', 
    id='train-button', 
    n_clicks=0,
)

update_button = html.Button(
    'Download datasets', 
    id='update-button', 
    n_clicks=0,
)

modal_window = dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle("About this app")),
                dbc.ModalBody(
                    [
                        html.H6("What is it ?"),
                        html.P("This dashboard predicts the power consumption in France for given dates. You can compare those predictions with the true power consumption provided by RTE-France (www.rte-france.com) and their own prediction."),                       
                        html.Hr(),

                        html.H6("What is behind ?"),
                        html.P("A small docker container running Dash for the dashboard and fbprophet for the prediction."),
                        html.Hr(),

                        html.H6("Where does the data come from ?"),
                        html.P("The dataset is comes from https://opendata.reseaux-energies.fr/ and under the 'Licence Ouverte v2.0 (Etalab)' license. Multiple providers:"),
                        html.Ul(
                            [
                                html.Li("Power : http://www.rte-france.com/fr/eco2mix/eco2mix"),
                                html.Li("Temperatures : http://www.weathernews.fr"),
                                html.Li("Weather : http://www.weathernews.fr"),
                            ],
                        ),
                        html.Hr(),

                        html.H6("How do you predict things?"),
                        html.P("The fbprophet library provides a time-series based prediction. The three models are trained on the whole consolidated dataset (except the last 52 weeks) to predict the power consumption."),
                        html.Ul(
                            [
                                html.Li("Basic : no regressors"),
                                html.Li("Temp : the average temperature in France per hour is added as a regressor"),
                                html.Li("Weather : multiple regressors are added such as the temperature, but also the wind speed, the humidity, etc"),
                            ],
                        ),
                        html.H6("How do I use it?"),
                        html.P("Try it ! Select the desired production dates by clicking on the daterange-picker or by zooming on the production graph. If you click on one of its lines, the power consumption for the next hour, day, week, month or year will be predicted. Please try the free provided models and check the RMSE value ;)"),                      

                    ]
                ),
            ],
            id="modal-window",
            size="xl",
            is_open=False,
        )

predict_next_dropdown = dcc.Dropdown(
    id="predict-next-dropdown",
    options = [
        {"label" : "Day", "value" : "1"},
        {"label" : "Week", "value" : "7"},
        {"label" : "Month", "value" : "31"},
        {"label" : "Year", "value" : "365"},
    ],
    value="1"
)

predict_next_box = dbc.Row(
    [
        dbc.Col(
            "Predict next :", 
            md=6, 
            align="center"
        ),
        dbc.Col(
            predict_next_dropdown, 
            md=6, 
            align="center"
        ),
    ]
)


model_dropdown = dcc.Dropdown(
    id="model-dropdown",
    options = [],
)

model_box = dbc.Row(
    [
        dbc.Col(
            "Select model :", 
            md=4, 
            align="center"
            ),
        dbc.Col(
            model_dropdown, 
            md=8, 
            align="center"
            ),
    ]
)

daterange_picker = html.Div(
    dcc.DatePickerRange(
        "Selected dates :",
        id='daterange-picker',
    )
)

date_box = dbc.Row(
    [
        dbc.Col(
            "Select dates :", 
            md=4, 
            align="center"
            ),
        dbc.Col(
            daterange_picker, 
            md=8, 
            align="center"
            ),
    ]
)


repartitions_graph = dcc.Graph(
                            id='repartitions-graph', 
                            style={
                                'height': '33vh'
                                }
                        )

productions_graph = dbc.Spinner(
                        dcc.Graph(
                            id='productions-graph', 
                            style={
                                'height': '33vh'
                                }
                        ),
                        color="primary"
                    )

predictions_graph = dbc.Spinner(
                        dcc.Graph(
                            id='predictions-graph', 
                            style={
                                'height': '35vh'
                                }
                        ),
                        color="primary"
                    )

components_graph = dbc.Spinner(
                        dcc.Graph(
                            id='components-graph', 
                            style={
                                'height': '35vh'
                                }
                        ),
                        color="primary"
                    )

header = dbc.Row(
        [
            dbc.Col(
                [
                    html.H2(
                        title
                    ),
                    html.H6(
                        subtitle
                    ),                    
                ], 
                width=True, 
                md=9,
            ),

            dbc.Col(
                update_button, 
                md=1, 
                align="center"
            ),   
            dbc.Col(
                train_button, 
                md=1, 
                align="center"
            ),     
            dbc.Col(
                learn_more_button, 
                md=1, 
                align="center"
            ),         

        ], 
        align="end",
        style={
            'margin-top' : '25px',
            'margin-bottom' : '25px'
            }
    )


analysis_card = html.Div(
        dbc.Card(
                dbc.CardBody(
                    children=[
                        dbc.CardHeader(
                            dbc.Row(
                                [
                                    dbc.Col(
                                        "Production analysis", 
                                        md=3, 
                                        align="center",
                                        style={
                                            "font-weight" : "bold",
                                        }
                                    ),
                                    dbc.Col(
                                        md=5,
                                    ),
                                    dbc.Col(
                                        date_box,
                                        md=4
                                    ),
                                ],
                            ),
                        ),
                        dbc.Row(
                            [
                                dbc.Col(
                                    productions_graph,
                                    md=6,
                                    align="center"
                                ),
                                dbc.Col(
                                    md=1,
                                ),
                                dbc.Col(
                                    repartitions_graph,
                                    md=5,
                                    align="center"
                                ),
                            ],
                        ),
                    ],
                ),
                style={
                    "margin-top" : "0px"
                    },
            ),
            style={
                "margin" : "0.5rem", 
                "padding" : "0.0rem",
                "margin-top" : "0px"}
    )

prediction_card = html.Div(
            dbc.Card(
                dbc.CardBody(
                    children=[
                        dbc.CardHeader(
                            dbc.Row(
                                [
                                    dbc.Col(
                                        "Consumption prediction (Click on one line of the production graph to make a prediction ! )", 
                                        id="predictions-header", 
                                        md=5, 
                                        align="center",
                                        style={
                                            "font-weight" : "bold",
                                        }
                                        ),
                                    dbc.Col(
                                        md=2
                                        ),
                                    dbc.Col(
                                        predict_next_box, 
                                        md=2, 
                                        align="center"
                                        ),
                                    dbc.Col(
                                        model_box, 
                                        md=3, 
                                        align="center"
                                        ),

                                ]
                                )
                            ),
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        predictions_graph
                                    ],
                                    md=6,
                                    style={
                                        "justify" : "center"
                                    }
                                ),
                                dbc.Col(
                                    md=1,
                                ),
                                dbc.Col(
                                    [
                                        components_graph
                                    ],
                                    md=5
                                )
                            ]
                        ),
                    ],
                )
            ),
            style={
                "margin" : "0.5rem"
                }
    )

layout_composition = dbc.Container(
    [
        header,
        dbc.Row(
            dbc.Col(
                [
                    analysis_card,
                    prediction_card,
                ],
                md=12,
            )
        ),
        dbc.Row(footer),
        modal_window,
    ],
    fluid=True,
    style = {
        "height": "100hv",
    }
)