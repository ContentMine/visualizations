# factheatmap.py

import os

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from bokeh.layouts import column, row
from bokeh.plotting import figure, show
from bokeh.models import ColumnDataSource, HoverTool, Legend
from bokeh.models.widgets import Slider, Select, TextInput, DataTable, TableColumn, Paragraph, Div, RadioGroup, Button
from bokeh.io import curdoc, output_notebook, output_file, save
from bokeh.charts import HeatMap, bins, vplot, TimeSeries
from bokeh.models import FixedTicker, SingleIntervalTicker, TapTool, BoxSelectTool, ResetTool

import bokeh.palettes as palettes
from bokeh.resources import INLINE, CDN

import itertools

from cmvisualizations.preprocessing import preprocessing
from cmvisualizations import config


# setup

resources = INLINE
colors=palettes.Dark2_8


# load initial data

df = preprocessing.get_preprocessed_df()


# Create Input controls

text_input = TextInput(value="erlotinib, zika, myopathy, retinitis",
                        title="Enter up to 8 comma separated facts:", width=600)
go_button = Button(label="Update", width=70)

timegroupoptionsmapper = {0:"A", 1:"M", 2:"D"}
trendingoptionsmapper = {0:False, 1:True}
timegroupoptions = ["Year", "Month", "Day"]
timegroup = RadioGroup(labels=timegroupoptions, active=2)

def get_ts_data():
    requested_facts = text_input.value.split(",")[:8]
    requested_facts = [f.strip() for f in requested_facts]
    req_df = preprocessing.get_facts_from_list(df, requested_facts)
    ts = preprocessing.make_timeseries(req_df)
    ts.columns = ts.columns.droplevel(0)
    ts = ts.groupby(pd.TimeGrouper(freq=timegroupoptionsmapper[timegroup.active])).sum()
    return ts


def update():
    new_data = get_ts_data()
    new_columns = new_data.columns.tolist()
    new_data.columns = [str(r) for r in list(range(0,len(new_columns)))]
    empty_nr = 8 - len(new_columns)

    new_legends = []
    for j, new_col in enumerate(new_data.columns):
        new_source = ColumnDataSource(dict(x=new_data[new_col].index,
                                           y=new_data[new_col].values))
        rend = fig.renderers[4:-1][j]
        rend.data_source.data=new_source.data
        new_legends.append((str(new_columns[j]), [rend]))
    fig.legend[0].update(legends=new_legends)
    for j in range(empty_nr, 8):
        new_source = ColumnDataSource(dict(x=[],
                                           y=[]))
        rend = fig.renderers[4:-1][j]
        rend.data_source.data=new_source.data

fig = figure(title=None, toolbar_location=None, tools=[],
           x_axis_type="datetime",
           width=600, height=300)
legends = []
for i in range(0,8):
    l = fig.line(x=[], y=[],
             color=colors[i])
    legends.append((str(i), [l]))

fig.legend.background_fill_alpha = 0
fig.background_fill_color = "whitesmoke"

legend = Legend(legends=legends, location=(0, 0))

fig.add_layout(legend, "right")


controls = [text_input, go_button]
go_button.on_click(update)
#timegroup.on_change("value", update)

# initial update
update()

### LAYOUT

content_filename = "description.html"
description = Div(text=open(content_filename).read(), render_as_text=False, width=600)


inputs = row(*controls)
layout = column(description, column(inputs, fig))
curdoc().add_root(layout)
curdoc().title = "Exploring co-occurrences of fact between facets"
