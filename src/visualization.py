import plotly.express as px
import plotly.graph_objs as go
import numpy as np
from fbprophet.plot import plot_components_plotly
from plotly.subplots import make_subplots

class Visualization():

    def __init__(self):
        
        self.template = "plotly_white"

    def reorganize_components(self, components):

        COLORS = ["#ef476f", "#073b4c", "#118ab2", "#06d6a0", "#ffd166", ]
        ORDER = ["Yearly", "Weekly", "Daily", "Extra_regressors_additive"]

        plotly_order = [component.get("name").capitalize() for component in components]

        components_as_dict = {}

        for color, order in zip(COLORS, ORDER):
            if order in plotly_order:
                index_of_figure = plotly_order.index(order)
                components_as_dict[order] = {
                    "color": color,
                    "data" : components[index_of_figure]
                }
        
        num_rows = 2
        num_cols = 2 if len(components_as_dict) <= 4 else 3

        components_figure = make_subplots(
            rows=num_rows, cols=num_cols,
            subplot_titles = ORDER,
        )
        
        for idx, value in enumerate(components_as_dict.values()):

            plotly_figure = go.Scatter(value.get("data"))
            plotly_color = value.get("color")

            plotly_figure.line.color = plotly_color
                    
            (row, col) = divmod(idx , num_cols)

            components_figure.append_trace(plotly_figure, row=row+1, col=col+1)
            
        return components_figure

    def px_pie(self, names=None, values=None, hole=0.3):
        
        return px.pie( 
            names = names,
            values = values,
            hole=hole        
        ) 

    def px_lines(self, df=None, x=None, y=None, color=None):

        return px.line(
            df,
            x=x,
            y=y,
            color=color
        )

    def go_lines(self, df=None, x=None, y=None, color=None, reverse_last=False, name=None, fill=None, mode="lines"):

        if reverse_last:

            x[-1] = x[-1][::-1]
            y[-1] = y[-1][::-1]

            x = np.concatenate(x)
            y = np.concatenate(y)
        
        return go.Scatter(
            x=x,
            y=y,
            fill=fill,
            line=dict(color=color),
            name=name,
            mode=mode,
            marker_size=3
        )

    def to_go_figure(self, figs):
        
        return go.Figure(figs).update_layout(
            template=self.template,
        )

    def update_components_ticks(self, fig, **kwargs):
        return fig.update_layout(
            xaxis_tickformat = kwargs.get("xaxis_tickformat", None),
            xaxis2_tickformat = kwargs.get("xaxis2_tickformat", None),
            xaxis3_tickformat = kwargs.get("xaxis3_tickformat", None),
            xaxis4_tickformat = kwargs.get("xaxis4_tickformat", None),
            yaxis_tickformat = kwargs.get("yaxis_tickformat", None),
            yaxis2_tickformat = kwargs.get("yaxis2_tickformat", None),
            yaxis3_tickformat = kwargs.get("yaxis3_tickformat", None),
            yaxis4_tickformat = kwargs.get("yaxis4_tickformat", None),
        )

    def update_layout(self, fig, showlegend=True, title=None, margin=None, xaxis_title=None, yaxis_title=None, **kwargs):

        if not margin:
            margin=dict(l=2, r=2, t=35, b=5)

        return fig.update_layout(
            showlegend=showlegend,
            xaxis_title=xaxis_title,
            yaxis_title=yaxis_title,
            template=self.template,
            margin=margin,
            title=title,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.35,
                xanchor="left",
                x=0.0
            )
        ).update_yaxes(
            rangemode="tozero",
        )