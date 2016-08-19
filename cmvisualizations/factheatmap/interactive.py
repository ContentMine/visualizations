# factheatmap.py

import os

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from bokeh.layouts import column, row
from bokeh.plotting import Figure, show
from bokeh.models import ColumnDataSource, HoverTool, HBox, VBox, VBoxForm
from bokeh.models.widgets import Slider, Select, TextInput, DataTable, TableColumn, Paragraph
from bokeh.io import curdoc, output_notebook, output_file, save
from bokeh.charts import HeatMap, bins, vplot
from bokeh.models import FixedTicker, SingleIntervalTicker, TapTool, BoxSelectTool, ResetTool

import bokeh.palettes as palettes
import bokeh.resources as resources

import itertools

from cmvisualizations.preprocessing import preprocessing
from cmvisualizations import config


coocc_features = preprocessing.get_coocc_features()

# Create Input controls
pluginoptions = sorted(coocc_features.index.levels[0])
top_n = Slider(title="Number of top-n items to display", value=20, start=5, end=50, step=5)
x_axis = Select(title="X Axis", options=sorted(pluginoptions), value=pluginoptions[0])
y_axis = Select(title="Y Axis", options=sorted(pluginoptions), value=pluginoptions[0])


def select_facts(coocc_features):
    logsource = np.log(coocc_features.ix[x_axis.value][y_axis.value]+1)
    x_sorted = logsource.ix[logsource.sum(axis=1).sort_values(ascending=False).index]
    y_sorted = x_sorted.T.ix[x_sorted.T.sum(axis=1).sort_values(ascending=False).index]
    logsource = y_sorted.T
    n_cols = len(logsource.columns)
    n_rows = len(logsource.index)
    df = pd.DataFrame()
    df["x"] = list(itertools.chain.from_iterable(list(itertools.repeat(i, times=n_cols)) for i in logsource.index))
    df["y"] = list(itertools.chain.from_iterable(list(itertools.repeat(logsource.stack().index.levels[1].values, times=n_rows))))
    df["counts"] = logsource.stack().values
    df["raw"] = df["counts"].map(np.exp)-1
    df.sort_values("counts", ascending=False, inplace=True)
    bins = np.linspace(df.counts.min(), df.counts.max(), 10) # bin labels must be one more than len(colorpalette)
    df["color"] = pd.cut(df.counts, bins, labels = list(reversed(palettes.Blues9)), include_lowest=True)

    selected_x = df.groupby("x").sum().sort_values("counts", ascending=False)[:top_n.value].index.values
    selected_y = df.groupby("y").sum().sort_values("counts", ascending=False)[:top_n.value].index.values
    selected = df[
        (df.x.isin(selected_x) &
         df.y.isin(selected_y) )
    ]
    return selected, selected_x, selected_y

def update(attrname, old, new):
    new_selected, selected_x, selected_y = select_facts(coocc_features)

    p.xaxis.axis_label = x_axis.value
    p.yaxis.axis_label = y_axis.value
    p.title.text = "Top %d fact co-occurrences selected" % top_n.value
    src = ColumnDataSource(dict(
        x=new_selected["x"].astype(object),
        y=new_selected["y"].astype(object),
        color=new_selected["color"].astype(object),
        raw=selected["raw"].astype(int)))
    source.data.update(src.data)
    p.x_range.update(factors=selected_x.tolist())
    p.y_range.update(factors=selected_y.tolist())

selected, selected_x, selected_y = select_facts(coocc_features)
source = ColumnDataSource(data=dict(x=[], y=[], color=[], raw=[]))
source.data.update(ColumnDataSource(dict(
    x=selected["x"].astype(object),
    y=selected["y"].astype(object),
    color=selected["color"].astype(object),
    raw=selected["raw"].astype(int)))
    .data)

TOOLS="tap, box_select, reset"

p = Figure(plot_height=900, plot_width=900, title="",
           tools=TOOLS, toolbar_location="above",
           x_range=selected_x.tolist(), y_range=selected_x.tolist())
p.rect(x="x", y="y", source=source, color="color", width=1, height=1)
p.xaxis.major_label_orientation = np.pi/4
p.yaxis.major_label_orientation = np.pi/4

table_columns = [TableColumn(field="x", title="X-axis facts"),
                 TableColumn(field="y", title="Y-axis facts"),
                 TableColumn(field="raw", title="Counts")]
data_table = DataTable(source=source, columns=table_columns, width=400, height=900)


controls = [top_n, x_axis, y_axis]
for control in controls:
    control.on_change('value', update)

inputs = HBox(VBoxForm(*controls), width=300)

update(None, None, None) # initial load of the data

inputs = column(*controls)
layout = row(column(inputs), p, data_table)
curdoc().add_root(layout)
curdoc().title = "Exploring co-occurrences of fact between facets"

show(curdoc())
