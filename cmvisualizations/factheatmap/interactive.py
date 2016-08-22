# factheatmap.py

import os

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from bokeh.layouts import column, row
from bokeh.plotting import Figure, show
from bokeh.models import ColumnDataSource, HoverTool
from bokeh.models.widgets import Slider, Select, TextInput, DataTable, TableColumn, Paragraph, Div
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
top_n = Slider(title="Number of top-n items to display", value=10, start=5, end=25, step=5)
x_axis_selector = Select(title="X Axis", options=sorted(pluginoptions), value=pluginoptions[2])
y_axis_selector = Select(title="Y Axis", options=sorted(pluginoptions), value=pluginoptions[1])


def prepare_facts(facets):
    factsets = {}
    for x_axis, y_axis in itertools.product(facets, repeat=2):
        subset = make_subset(coocc_features, x_axis, y_axis)
        factsets[(x_axis, y_axis)] = subset
    return factsets

def make_subset(coocc_features, x_axis, y_axis):
    logsource = np.log(coocc_features.ix[x_axis][y_axis]+1)
    x_sorted = logsource.ix[logsource.sum(axis=1).sort_values(ascending=False).index]
    y_sorted = x_sorted.T.ix[x_sorted.T.sum(axis=1).sort_values(ascending=False).index]
    logsource = y_sorted.T.ix[:top_n.end, :top_n.end]
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

    new_x_factors = logsource.index.values.tolist()
    new_y_factors = logsource.columns.values.tolist()

    return df, new_x_factors, new_y_factors

factsets = prepare_facts(pluginoptions)

def get_subset(x_axis, y_axis):
    return factsets.get((x_axis, y_axis))

def update(attrname, old, new):
    new_selected, new_x_factors, new_y_factors = get_subset(x_axis_selector.value, y_axis_selector.value)

    p.xaxis.axis_label = x_axis_selector.value
    p.yaxis.axis_label = y_axis_selector.value
    p.title.text = "Top %d fact co-occurrences selected" % top_n.value

    src = ColumnDataSource(dict(
        x=new_selected["x"].astype(object),
        y=new_selected["y"].astype(object),
        color=new_selected["color"].astype(object),
        raw=new_selected["raw"].astype(int)))
    source.data.update(src.data)

    p.x_range.update(factors=new_x_factors[:top_n.value])
    p.y_range.update(factors=new_y_factors[:top_n.value])

source = ColumnDataSource(data=dict(x=[], y=[], color=[], raw=[]))
selected, new_x_factors, new_y_factors = get_subset(x_axis_selector.value, y_axis_selector.value)

TOOLS="tap, box_select, reset"

p = Figure(plot_height=700, plot_width=700, title="",
           tools=TOOLS, toolbar_location="above",
           x_range=new_x_factors[:top_n.value],  y_range=new_y_factors[:top_n.value])
p.rect(x="x", y="y", source=source, color="color", width=0.95, height=0.95, name="glyphs")
p.xaxis.major_label_orientation = np.pi/4
p.yaxis.major_label_orientation = np.pi/4
p.xgrid.visible = False
p.ygrid.visible = False

renderer = p.select(name="glyphs")[0]
renderer.selection_glyph = renderer.glyph
renderer.nonselection_glyph = renderer.glyph

table_columns = [TableColumn(field="x", title="X-axis facts"),
                 TableColumn(field="y", title="Y-axis facts"),
                 TableColumn(field="raw", title="Counts")]
data_table = DataTable(source=source, columns=table_columns, width=400, height=600)


controls = [top_n, x_axis_selector, y_axis_selector]
for control in controls:
    control.on_change('value', update)

update(None, None, None) # initial load of the data

### LAYOUT

content_filename = os.path.join(os.path.dirname(__file__), "description.html")

description = Div(text=open(content_filename).read(), render_as_text=False, width=600)


inputs = row(*controls)
layout = column(inputs, row(p, data_table))
curdoc().add_root(column(description, layout))
curdoc().title = "Exploring co-occurrences of fact between facets"

show(curdoc())
