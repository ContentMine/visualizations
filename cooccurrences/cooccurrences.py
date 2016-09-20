# factheatmap.py

import pandas as pd
import numpy as np

from bokeh.layouts import column, row, WidgetBox
from bokeh.plotting import Figure, show
from bokeh.models import ColumnDataSource, HoverTool, OpenURL, TapTool
from bokeh.models.widgets import Slider, Select, TextInput, DataTable, TableColumn, Paragraph, Div
from bokeh.io import curdoc, output_notebook, output_file, save
from bokeh.charts import HeatMap, bins, vplot
from bokeh.models import FixedTicker, SingleIntervalTicker, TapTool, BoxSelectTool, ResetTool

import bokeh.palettes as palettes
import bokeh.resources as resources

import pickle
import gzip



with gzip.open("coocc_factsets.pklz", "rb") as infile:
    factsets = pickle.load(infile)


with gzip.open("../wikidata_dict.pklz", "rb") as infile:
    wikidataIDs = pickle.load(infile)

# Create Input controls
pluginoptions = sorted([f[0] for f in list(factsets.keys())])
top_n = Slider(title="Number of top-n items to display", value=10, start=5, end=25, step=5)
dictionary_selector = Select(title="Dictionary", options=sorted(pluginoptions), value=pluginoptions[2])

def get_subset(x_axis, y_axis):
    return factsets.get((x_axis, y_axis))

def update(attrname, old, new):
    new_selected, new_x_factors, new_y_factors = get_subset(dictionary_selector.value, dictionary_selector.value)
    bins = np.linspace(new_selected.counts.min(), new_selected.counts.max(), 10) # bin labels must be one more than len(colorpalette)
    new_selected["color"] = pd.cut(new_selected.counts, bins, labels = list(reversed(palettes.Blues9)), include_lowest=True)
    new_selected["wikidataID"] = new_selected["x"].map(lambda x: wikidataIDs.get(x))

    p.xaxis.axis_label = dictionary_selector.value
    p.yaxis.axis_label = dictionary_selector.value
    p.title.text = "Top %d fact co-occurrences selected" % top_n.value

    src = ColumnDataSource(dict(
        x=new_selected["x"].astype(object),
        y=new_selected["y"].astype(object),
        color=new_selected["color"].astype(object),
        wikidataID=new_selected["wikidataID"],
        counts=new_selected["counts"].astype(int),
        raw=new_selected["raw"].astype(int)))
    source.data.update(src.data)

    p.x_range.update(factors=new_x_factors[:top_n.value])
    p.y_range.update(factors=new_y_factors[:top_n.value])


source = ColumnDataSource(data=dict(x=[], y=[], color=[], raw=[], wikidataID=[], counts=[]))
selected, new_x_factors, new_y_factors = get_subset(dictionary_selector.value, dictionary_selector.value)


TOOLS="tap, reset"

hover = HoverTool(names = ["glyphs"],
                  tooltips=[("Cooccurring", "@x, @y"),
                            ("Counts", "@counts"),
                            ("wikidataID for this item (x-axis)", "@wikidataID")])

p = Figure(plot_height=700, plot_width=700, title="",
           tools=TOOLS, toolbar_location="above",
           x_range=new_x_factors[:top_n.value],  y_range=new_y_factors[:top_n.value])
p.add_tools(hover)

update(None, None, None) # initial load of the data
rects = p.rect(x="x", y="y", source=source, color="color", width=0.95, height=0.95, name="glyphs")
p.xaxis.major_label_orientation = np.pi/4
p.yaxis.major_label_orientation = np.pi/4
p.xgrid.visible = False
p.ygrid.visible = False

url = "https://www.wikidata.org/wiki/@wikidataID"
taptool = p.select(type=TapTool)
taptool.callback = OpenURL(url=url)

renderer = p.select(name="glyphs")[0]
renderer.selection_glyph = renderer.glyph
renderer.nonselection_glyph = renderer.glyph
renderer.hover_glyph = renderer.glyph

# table_columns = [TableColumn(field="x", title="X-axis facts"),
#                  TableColumn(field="y", title="Y-axis facts"),
#                  TableColumn(field="raw", title="Counts")]
# data_table = DataTable(source=source, columns=table_columns, width=400, height=600)


top_n.on_change('value', update)
dictionary_selector.on_change('value', update)


### LAYOUT
description = Div(text=open("description.html").read(), render_as_text=False, width=800)

inputs = row(top_n, dictionary_selector)
layout = column(description, inputs, p)
curdoc().add_root(layout)
curdoc().title = "Exploring co-occurrences of facts"
