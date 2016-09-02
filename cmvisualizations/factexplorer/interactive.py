# factheatmap.py

import os

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from bokeh.layouts import column, row
from bokeh.plotting import Figure, show
from bokeh.models import ColumnDataSource, HoverTool
from bokeh.models.widgets import Slider, Select, TextInput, RadioGroup, Paragraph, Div
from bokeh.io import curdoc, output_notebook, output_file, save
from bokeh.charts import HeatMap, bins, vplot
from bokeh.models import FixedTicker, SingleIntervalTicker, TapTool, BoxSelectTool, ResetTool

import bokeh.palettes as palettes
import bokeh.resources as resources

import itertools

from cmvisualizations.preprocessing import preprocessing
from cmvisualizations import config


df = preprocessing.get_preprocessed_df()

# Create Input controls

desired_facts = TextInput()

# Create Input controls
timegroupoptionsmapper = {0:"A", 1:"M", 2:"D"}
timegroupoptions = ["Year", "Month", "Day"]
timegroup = RadioGroup(labels=timegroupoptions, active=2)


def get_ts_data():
    text_inputs = desired_facts.value.split(",")
    sub_dfs = [preprocessing.get_facts_from_list(df, input_) for text_input in text_inputs]
    ts = [preprocessing.make_timeseries(sub_df) for sub_df in sub_dfs]
    return ts


def update_ts(attrname, old, new):
    ts = get_ts_data()
    new_ts = ts.groupby(pd.TimeGrouper(freq=timegroupoptionsmapper[timegroup.active])).sum().fillna(0)

    new_ts_sources = ColumnDataSource(new_ts)
    for old, new in zip(ts_sources, new_ts_sources):
        old.data.update(new.data)

    new_ts_point_sources = [ColumnDataSource(dict(date=[new_ts[l].idxmax()],
                                                   y=[new_ts[l].max()],
                                                   text=[str(int(new_ts[l].max()))]
                                                   )
                                              )
                                              for l in new_ts.columns.tolist()]

    for old, new in zip(ts_point_sources, new_ts_point_sources):
        old.data.update(new.data)

for desired_fact in desired_facts:
    desired_fact.on_change("value", update_ts)

ts_sources = [ColumnDataSource(dict(date=initial_subset[0].index, y=initial_subset[0][l])) for l in initial_subset[0].columns.tolist()]
ts_point_sources = [ColumnDataSource(dict(date=[initial_subset[0][l].idxmax()],
                                           y=[initial_subset[0][l].max()],
                                           text=[str(int(initial_subset[0][l].max()))]
                                           )
                                      )
                                      for l in initial_subset[0].columns.tolist()[:top_n.value]]

def make_plots(linesources, pointsources):
    plots = []
    i=0
    for linesource, pointsource in zip(linesources, pointsources):
        fig = Figure(title=None, toolbar_location=None, tools=[],
                   x_axis_type="datetime",
                   width=300, height=90)

        fig.xaxis.visible = False
        if i in [0, 9] :
            fig.xaxis.visible = True
            fig.height = 110
        fig.yaxis.visible = False
        fig.xgrid.visible = True
        fig.ygrid.visible = False
        fig.min_border_left = 10
        fig.min_border_right = 10
        fig.min_border_top = 10
        fig.min_border_bottom = 10
        if not i in [0, 9]:
            fig.xaxis.major_label_text_font_size = "0pt"
        #fig.yaxis.major_label_text_font_size = "0pt"
        fig.xaxis.major_tick_line_color = None
        fig.yaxis.major_tick_line_color = None
        fig.xaxis.minor_tick_line_color = None
        fig.yaxis.minor_tick_line_color = None
        fig.background_fill_color = "whitesmoke"

        fig.line(x='date', y="y", source=linesource)
        fig.circle(x='date', y='y', size=5, source=pointsource)
        fig.text(x='date', y='y', text='text', y_offset=20, text_font_size='7pt', source=pointsource)

        fig.title.align = 'left'
        fig.title.text_font_style = 'normal'

        plots.append(fig)
        i+=1
    return plots

ts_arrangement = make_plots(ts_sources, ts_point_sources)

controls = [desired_facts, timegroup]

inputs = row(*controls)


### LAYOUT

content_filename = os.path.join(os.path.dirname(__file__), "description.html")
description = Div(text=open(content_filename).read(), render_as_text=False, width=900)

layout = column(description, inputs, row(column(ts_arrangement)))
curdoc().add_root(layout)
