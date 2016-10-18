# main.py

import string
import pandas as pd

from bokeh.layouts import column, row
from bokeh.plotting import Figure, show
from bokeh.embed import standalone_html_page_for_models
from bokeh.models import ColumnDataSource, HoverTool, HBox, VBox
from bokeh.models.ranges import Range1d
from bokeh.models import LinearAxis
from bokeh.models.widgets import Slider, Select, TextInput, RadioGroup, Paragraph, Div
from bokeh.io import curdoc, save
from bokeh.charts import HeatMap, bins, output_file, vplot, TimeSeries, Line, Bar
from bokeh.charts.operations import blend
from bokeh.charts.attributes import cat
from bokeh.models import FixedTicker, SingleIntervalTicker, ColumnDataSource, DataRange1d
from bokeh.layouts import widgetbox
from bokeh.layouts import gridplot
import bokeh.palettes as palettes
from bokeh.resources import INLINE, CDN

import pickle
import gzip

with gzip.open("../data/journal_features.pklz", "rb") as infile:
    journ_raw = pickle.load(infile)

journal_dist = journ_raw.drop_duplicates("pmcid").groupby("journalTitle").count().sort_values(by="term", ascending=False)
journal_dist["cumulative"] = (journal_dist["term"]/journal_dist["term"].sum()).cumsum()
clean_index = [i[:30] for i in journal_dist.index.tolist()]
clean_index = [s.translate(str.maketrans({p:"" for p in string.punctuation})) for s in clean_index]
journal_dist.index = clean_index
journal_dist["journalTitle"] = journal_dist.index

resources = INLINE
colors=palettes.Paired10

# fig = Figure(plot_height=400, plot_width=700, title="",
#            toolbar_location="above",
#            x_range=journal_dist.index.tolist())
# fig.xaxis.major_label_orientation = pd.np.pi/4
# fig.yaxis.major_label_orientation = pd.np.pi/4
# fig.rect(x=journal_dist.index.tolist(), y = [y/2 for y in journal_dist.tolist()],
#             width=0.9, height = journal_dist.tolist())
fig = Bar(journal_dist[journal_dist['term'] > 1], plot_height=400, plot_width=800,
            values=blend('term', labels_name='journalTitle'),
            label=cat(columns='journalTitle', sort=False),
            legend=None)
fig.toolbar_location = "above"
fig.extra_y_ranges = {"Cumulative": Range1d(start=0, end=1)}
fig.add_layout(LinearAxis(y_range_name="Cumulative"), 'right')
fig.line(journal_dist[journal_dist['term'] > 1].index.tolist(),
            journal_dist[journal_dist['term'] > 1]["cumulative"].values.tolist(),
            line_width=2,
            y_range_name='Cumulative')

### LAYOUT

layout = column(fig)
curdoc().add_root(layout)
curdoc().title = "Exploring aggregated counts of facts over dictionaries"
