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


factsets = preprocessing.get_coocc_factsets()

# Create Input controls
pluginoptions = sorted([f[0] for f in list(factsets.keys())])
top_n = Slider(title="Number of top-n items to display", value=10, start=5, end=25, step=5)
facet_selector = Select(title="Facet", options=sorted(pluginoptions), value=pluginoptions[2])



def get_subset(x_axis, y_axis):
    return factsets.get((x_axis, y_axis))

def update(attrname, old, new):
    new_selected, new_x_factors, new_y_factors = get_subset(facet_selector.value, facet_selector.value)
    bins = np.linspace(new_selected.counts.min(), new_selected.counts.max(), 10) # bin labels must be one more than len(colorpalette)
    new_selected["color"] = pd.cut(new_selected.counts, bins, labels = list(reversed(palettes.Blues9)), include_lowest=True)

    p.xaxis.axis_label = facet_selector.value
    p.yaxis.axis_label = facet_selector.value
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
selected, new_x_factors, new_y_factors = get_subset(facet_selector.value, facet_selector.value)

TOOLS="tap, box_select, reset"

p = Figure(plot_height=700, plot_width=700, title="",
           tools=TOOLS, toolbar_location="above",
           x_range=new_x_factors[:top_n.value],  y_range=new_y_factors[:top_n.value])
update(None, None, None) # initial load of the data
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


controls = [top_n, facet_selector]
for control in controls:
    control.on_change('value', update)


### LAYOUT

content_filename = os.path.join(os.path.abspath(os.path.dirname("__file__")), "description.html")
description = Div(text=open(content_filename).read(), render_as_text=False, width=600)

inputs = row(*controls)
layout = column(inputs, row(p, data_table))
curdoc().title = "Exploring co-occurrences of fact between facets"
curdoc().add_root(column(description, layout))
