# Libraries
import argparse
import pandas as pd
import numpy as np
from flask import Flask
from datetime import datetime
from datetime import timedelta
from dash import Dash, html, Input, Output, State, ctx

# Modules
import layout
import converter
from pipeline import Pipeline
from visualization import Visualization

# Constants
from config import COL_VISUALISATION_PRODUCTION

# Server conf
server = Flask(__name__)



# Dash App
app = Dash(
    __name__, 
    server=server, 
    meta_tags=[{"name": "viewport", "content": "width=device-width"}],
    external_stylesheets=layout.stylesheets,
    title=layout.title
)

# Dash layout
app.layout = layout.layout_composition

# Visualisation
vis = Visualization()

# Pipeline
pip = Pipeline()
pip.data_process()
pip.build_models()

@app.callback(
    [
        Output('predictions-graph', 'figure'),
        Output('components-graph', 'figure'),
        Output('predictions-header', 'children'),
    ],
    [
        Input('predict-next-dropdown', 'value'),
        Input('productions-graph', 'clickData'),
        State('daterange-picker', 'end_date'),
        Input('model-dropdown', 'value'),
    ],
    prevent_initial_call=True,
)
def update_predictions(delta_days, clickInfo, start, model_name):
    """Update the prediction graph

    Args:
        delta_days (str): timedelta to add to the start date
        clickInfo (dict): on click on the production graph
        start (str): start date
        model_name (str): name of the model

    Returns:
        _type_: _description_
    """

    # If the user click on the production graph, the date is used as start date
    if clickInfo:
        start = clickInfo['points'][0]['x']
        start = converter.date(start)
    # Otherwise, the start date is 123 days before the end date
    else:
        start = converter.date(start)
        start -= timedelta(days=123)
    
    # Get the end date according to the deltadate
    end = start + timedelta(days=int(delta_days))

    # Predict the values
    forecast, model = pip.data_test(start=start, end=end, extra_columns=["prevision_j1", ],  model_name=model_name)

    # Get the seasonalities
    plotly_components = model.get_plotly_components(forecast)._data

    # Calculate the RMSE value and set the text
    rmse_value = np.sqrt(np.mean(np.square(model.df_test.y.values - forecast.yhat.values)))
    rmse_text = f"Consumption prediction from {start.strftime('%Y-%m-%d')} to {end.strftime('%Y-%m-%d')} (RMSE : {rmse_value:0.0f})"

    # Reorganize the seasonality plot
    fig_components = vis.reorganize_components(plotly_components)
    fig_components = vis.update_layout(
        fig_components,
        showlegend=False
    )
    
    fig_components = vis.update_components_ticks(
        fig_components,
        xaxis_tickformat = '%b',
        xaxis2_tickformat = '%a',
        xaxis3_tickformat = '%H:%M',
        xaxis4_tickformat = '%b %d',
        yaxis_tickformat = '%:.0%f',
        yaxis2_tickformat = '%:.0%f',
        yaxis3_tickformat = '%:.0%f',
        yaxis4_tickformat = '%:.0%f',)

    # Plot the prediction
    fig_forecast = vis.go_lines(
        x=forecast.ds, 
        y=forecast.yhat,
        mode="markers",
        color="#3282B8",
        name="Prediction")

    # Plot the error band of the prediction
    fig_error = vis.go_lines(
        x=[forecast.ds, forecast.ds], 
        y=[forecast.yhat_upper, forecast.yhat_lower], 
        reverse_last=True,
        color="#BBE1FA",
        mode=None,
        fill="toself",
        name="Prediction error band")

    # Plot the true values provided by RTE-France
    fig_rte_values = vis.go_lines(
        x=model.df_test.ds, 
        y=model.df_test.y,
        color="#1B262C",
        name="RTE values")

    # # Plot the prediction made by RTE-France
    # fig_rte_prediction = vis.go_lines(
    #     x=model.df_test.index, 
    #     y=model.df_test["prevision_j1"],
    #     mode="markers",
    #     color="#0F4C75",
    #     name="RTE prediction J-1")

    # Add all the figures to the prediction figure
    fig_prediction = vis.to_go_figure([fig_forecast, fig_error, fig_rte_values])
    fig_prediction = vis.update_layout(
        fig_prediction,
        yaxis_title="Power consumption [MW]",)

    # Return the prediction figure, the seasonality figure and the rmse text
    return  [fig_prediction, fig_components, rmse_text]



@app.callback(
    Output('repartitions-graph', 'figure'),
    Input('productions-graph', 'hoverData'),
    Input('daterange-picker', 'end_date'),
)
def update_repartions(hoverData, date):
    """_summary_

    Args:
        hoverData (dict): if the cursor if above the productions graph
        date (str): _description_

    Returns:
        go.Figure: repartition figure
    """

    # If the cursor if over the production graph, we 
    if hoverData:
        date = hoverData['points'][0]['x']
    
    # Get the data according to the date and the columns to visualize
    df = pip.data_serve(date=date, columns=COL_VISUALISATION_PRODUCTION)

    # Melt the dataframe 
    df = pd.melt(df, ignore_index=True, value_vars=df.columns)

    # Represent the data as a pie figure
    fig_repartitions = vis.to_go_figure(vis.px_pie(names=df.variable, values=df.value))

    # Return the go figure
    return vis.update_layout(
        fig_repartitions,
    )

@app.callback(
    Output('footer-text', 'children'),
    [
        Input('train-button', 'n_clicks'),
    ]
)
def update_footer(_):
    """Train and update the options in the model-dropdown

    Args:
        useless (_type_): _description_

    Returns:
        [dict, value]: updated options and value by default
    """
    modification_datetime = pip.get_download_datetime()

    footer_text = "Original data downloaded from https://www.opendatasoft.com/fr/"
    footer_text += f" the {modification_datetime.date()}"
    footer_text += f" at {modification_datetime.time().strftime('%H:%M')}"

    return footer_text

@app.callback(
    Output('model-dropdown', 'options'),
    Output('model-dropdown', 'value'),
    [
        Input('train-button', 'n_clicks'),
    ]
)
def update_models(_):
    """Train and update the options in the model-dropdown

    Args:
        useless (_type_): _description_

    Returns:
        [dict, value]: updated options and value by default
    """

    # Build the options for the model-dropdown
    options = [
        {
            "label" : parameters.get('name'),
            "value" : name
        }
        for name, parameters in pip.models.items()
    ]

    # Return the options and select the first value by default
    return options, options[0].get("value")

@app.callback(
    Output('productions-graph', 'figure'),
    [
        Input('daterange-picker', 'start_date'),
        Input('daterange-picker', 'end_date'),  
        Input('update-button', 'n_clicks'),  
    ],
    prevent_initial_call=True,
)
def update_production(start, end, _):
    """_summary_

    Args:
        start (_type_): _description_
        end (_type_): _description_

    Returns:
        go.Figure: productions figure
    """

    # Update the dataset if asked
    if ctx.triggered_id == "update-button":
        pip.data_process(update=True, download=True, data_from="csv")

    # Get the data according to the date and the columns to visualize
    df = pip.data_serve(start=start, end=end, columns=COL_VISUALISATION_PRODUCTION)

    # Melt the dataframe 
    df = pd.melt(df, ignore_index=False, value_vars=df.columns)

    # Represent the data as a lines figure
    fig_production = vis.to_go_figure(vis.px_lines(x=df.index, y=df.value, color=df.variable))

    # Return the figure
    return vis.update_layout(
        fig_production,
        xaxis_title=None,
        yaxis_title="Power production by category [MW]",
        )

@app.callback(
    [
        Output('daterange-picker', 'min_date_allowed'),
        Output('daterange-picker', 'max_date_allowed'),
        Output('daterange-picker', 'start_date'),
        Output('daterange-picker', 'end_date'),
    ],
    [
        Input('productions-graph', 'relayoutData'),
    ]
)
def update_datepicker(zoom):
    """_summary_

    Args:
        zoom (_type_): _description_

    Returns:
        _type_: _description_
    """

    # Get the index of the dataframe
    index_serie = pip.data_serve(only_index=True)

    # Get the min and the max dates
    min_date_allowed = index_serie.min()
    max_date_allowed = index_serie.max()
    
    # The end date is the max_date_allowed
    end_date = max_date_allowed

    # The start date is 180 days before the end date
    start_date = end_date-timedelta(days=180)

    #Return the dates
    return min_date_allowed, max_date_allowed, start_date, end_date

def toggle_modal(n1, is_open):
    if n1:
        return not is_open
    return is_open


app.callback(
    Output("modal-window", "is_open"),
    Input("learn-more-button", "n_clicks"),
    State("modal-window", "is_open"),
)(toggle_modal)

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description='Provide options for the dashboard.')
    parser.add_argument('-i', "--ip-address",            
                    type=str,
                    default="localhost",
                    help='ip address of the dahsboard. By default, localhost is used')       

    parser.add_argument('-p', "--port",            
                    type=int,
                    default=8050,
                    help='port, 8050 by default')       

    parser.add_argument('-d', "--debug",            
                    action="store_true",
                    help='enable debugging')  

    args = parser.parse_args()

    #


    app.run_server(host=args.ip_address, port=args.port, debug=args.debug)
