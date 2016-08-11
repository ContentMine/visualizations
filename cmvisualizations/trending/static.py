# main.py

from os.path import dirname, join

from math import pi
import numpy as np
import pandas as pd
import glob

from bokeh.plotting import Figure, show
from bokeh.models import ColumnDataSource, HoverTool, HBox, VBox, VBoxForm
from bokeh.models.widgets import Slider, Select, TextInput, RadioGroup
from bokeh.io import curdoc, save
from bokeh.charts import HeatMap, bins, output_file, vplot, TimeSeries
from bokeh.models import FixedTicker, SingleIntervalTicker, ColumnDataSource, DataRange1d
from bokeh.layouts import widgetbox
from bokeh.layouts import gridplot
import bokeh.palettes as palettes
import bokeh.resources as resources

from itertools import chain, repeat

from hashlib import md5

from cmvisualizations.preprocessing import preprocessing


factsfile = "facts20160601-05.json".encode("utf-8")
metadatafile = "metadata20160601-05.json".encode("utf-8")
fname = md5(factsfile+metadatafile).hexdigest()

ts = preprocessing.get_timeseries_features()


# options:
# ts.groupby(pd.TimeGrouper(freq='A')).sum()
# ts[pluginoption]
# top_n_index = df.sort_values(ascending=False)[:top_n].index
# ts[pluginoption][top_n_index]
# manually enter facts to plot
# ts.T.xs("zika", level='term').T


def get_dataset(ts, facetvalue, top_nvalue, timegroupactive):
    if facetvalue == "All":
        ts_a = ts
        ts_a.columns = ts.columns.droplevel()
        selection = ts_a.groupby(pd.TimeGrouper(freq=timegroupoptionsmapper[timegroupactive])) \
                        .sum() \
                        .sort_values(ascending=False)[:top_nvalue] \
                        .index
        selected = ts_a[selection]
    else:
        selection = ts.groupby(pd.TimeGrouper(freq=timegroupoptionsmapper[timegroupactive])) \
                        .sum()[facetvalue] \
                        .sum().sort_values(ascending=False)[:top_nvalue] \
                        .index
        selected = ts[facetvalue][selection]
    return ColumnDataSource(selected)


# Create Input controls
pluginoptions = sorted(ts.columns.levels[0])
timegroupoptionsmapper = {0:"A", 1:"M", 2:"D"}
timegroupoptions = ["Year", "Month", "Day"]

top_n = Slider(title="Number of top-n items to display", value=5, start=1, end=20, step=1)
facet = Select(title="Facets", options=pluginoptions, value=pluginoptions[0])
timegroup = RadioGroup(labels=timegroupoptions, active=2)

colors = palettes.Paired12

def make_plot(facetvalue):
    p = Figure(title="", toolbar_location=None,
                x_axis_type="datetime")
    p.title.text = "Top %d fact occurrences selected" % top_n.value
    p.xaxis.axis_label = facetvalue
    p.yaxis.axis_label = "Count"

    source = get_dataset(ts, facetvalue, top_n.value, timegroup.active)
    i=0
    for l in source.data.keys():
        if l != 'firstPublicationDate':
            p.line(x="firstPublicationDate", y=l, source=source, line_color=colors[i],
                    legend=l)
            i+=1
    return p

plots = []
for facetvalue in pluginoptions:
    plots.append(make_plot(facetvalue))

grid = gridplot(plots, ncols=2, plot_width=600, plot_height=300)

# session = push_session(curdoc())
# script = autoload_server(plot, session_id=session.id)

show(grid)
output_file(fname+'static_timeseries.html')
save(obj=grid, filename=fname+'static_timeseries.html', resources=resources.INLINE)
