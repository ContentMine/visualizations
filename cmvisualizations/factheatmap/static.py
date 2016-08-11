# factheatmap.py

import os

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from bokeh.plotting import Figure, show
from bokeh.models import ColumnDataSource, HoverTool, HBox, VBox, VBoxForm
from bokeh.models.widgets import Slider, Select, TextInput
from bokeh.io import curdoc, output_notebook, output_file, save
from bokeh.charts import HeatMap, bins, vplot
from bokeh.models import FixedTicker, SingleIntervalTicker
from bokeh.layouts import gridplot

import bokeh.palettes as palettes
import bokeh.resources as resources

import itertools
from hashlib import md5

from cmvisualizations.preprocessing import preprocessing


factsfile = "facts20160601-05.json".encode("utf-8")
metadatafile = "metadata20160601-05.json".encode("utf-8")
fname = md5(factsfile+metadatafile).hexdigest()


coocc_features = preprocessing.get_coocc_features()

# Create Input controls
pluginoptions = sorted(coocc_features.index.levels[0])
top_n = Slider(title="Number of top-n items to display", value=20, start=5, end=50, step=5)
# x_axis = Select(title="X Axis", options=sorted(pluginoptions), value=pluginoptions[0])
# y_axis = Select(title="Y Axis", options=sorted(pluginoptions), value=pluginoptions[0])


def select_facts(coocc_features, x_axis, y_axis):
    logsource = np.log(coocc_features.ix[x_axis][y_axis]+1)

    n_cols = len(logsource.columns)
    n_rows = len(logsource.index)
    df = pd.DataFrame()
    df["x"] = list(itertools.chain.from_iterable(list(itertools.repeat(i, times=n_cols)) for i in logsource.index))
    df["y"] = list(itertools.chain.from_iterable(list(itertools.repeat(logsource.stack().index.levels[1].values, times=n_rows))))
    df["counts"] = logsource.stack().values
    df.sort_values("counts", ascending=False, inplace=True)
    bins = np.linspace(df.counts.min(), df.counts.max(), 10) # bin labels must be one more than len(colorpalette)
    df["color"] = pd.cut(df.counts, bins, labels = list(reversed(palettes.Blues9)), include_lowest=True)

    selected_x = df.groupby("x").sum().sort_values("counts", ascending=False)[:top_n.value].index.values
    selected_y = df.groupby("y").sum().sort_values("counts", ascending=False)[:top_n.value].index.values
    selected = df[
        (df.x.isin(selected_x) &
         df.y.isin(selected_y) )
    ]
    return selected


def make_plot(x_axis, y_axis):
    selected = select_facts(coocc_features, x_axis, y_axis)
    source = ColumnDataSource(data=dict(x=[], y=[], color=[]))
    source.data.update(ColumnDataSource(dict(
        x=selected["x"].astype(object),
        y=selected["y"].astype(object),
        color=selected["color"].astype(object)
        )).data)

    p = Figure(title="", toolbar_location=None,
               x_range=list(set(source.data.get("x"))), y_range=list(set(source.data.get("y"))))
    p.title.text = "Top %d fact co-occurrences selected" % top_n.value
    p.rect(x="x", y="y", source=source, color="color", width=1, height=1)
    p.xaxis.axis_label = x_axis
    p.yaxis.axis_label = y_axis
    p.xaxis.major_label_orientation = np.pi/4
    p.yaxis.major_label_orientation = np.pi/4
    p.x_range.update(factors=list(set(source.data.get("x"))))
    p.y_range.update(factors=list(set(source.data.get("y"))))

    return p

plots = []
for x_axis, y_axis in itertools.product(pluginoptions, repeat=2):
    plots.append(make_plot(x_axis, y_axis))

grid = gridplot(plots, ncols=2, plot_width=600, plot_height=600)

# session = push_session(curdoc())
# script = autoload_server(plot, session_id=session.id)

show(grid)
output_file(fname+'static_heatmap.html')
save(obj=grid, filename=fname+'static_heatmap.html', resources=resources.INLINE)
