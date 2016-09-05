# main.py
import os

from math import pi
import numpy as np
import pandas as pd
import os

from bokeh.layouts import column, row
from bokeh.plotting import Figure, show
from bokeh.embed import standalone_html_page_for_models
from bokeh.models import ColumnDataSource, HoverTool, HBox, VBox
from bokeh.models.widgets import Slider, Select, TextInput, RadioGroup, Paragraph, Div
from bokeh.io import curdoc, save
from bokeh.charts import HeatMap, bins, output_file, vplot, TimeSeries, Line
from bokeh.models import FixedTicker, SingleIntervalTicker, ColumnDataSource, DataRange1d
from bokeh.layouts import widgetbox
from bokeh.layouts import gridplot
import bokeh.palettes as palettes
from bokeh.resources import INLINE, CDN

from itertools import chain, repeat

from cmvisualizations.preprocessing import preprocessing
from cmvisualizations import config


dist = preprocessing.get_distribution_features()
share = (dist.T / dist.sum(axis=1)).T
#dist["date"] = dist.index
facets = sorted(dist.columns.tolist())
resources = INLINE
colors=palettes.Paired10


ts_abs = TimeSeries(dist, tools="pan,wheel_zoom,reset", active_scroll='wheel_zoom',
                        width=800, height=400,
                        title='Frequencies of facets - absolute counts', legend=True)
ts_abs.legend.orientation = "horizontal"
ts_abs.legend.location = "top_center"
ts_abs.legend.background_fill_alpha = 0
ts_abs.legend.border_line_alpha = 0
ts_abs.tools[2].reset_size=False


ts_share = TimeSeries(share, tools="pan,wheel_zoom,reset", active_scroll='wheel_zoom',
                        width=800, height=400,
                        title='Frequencies of facets - relative share', legend=True)
ts_share.x_range = ts_abs.x_range
ts_share.legend.orientation = "horizontal"
ts_share.legend.location = "top_center"
ts_share.legend.background_fill_alpha = 0
ts_share.legend.border_line_alpha = 0
ts_share.tools[2].reset_size=False

### LAYOUT

content_filename = os.path.join("distributions", "description.html")
description = Div(text=open(content_filename).read(), render_as_text=False, width=900)

layout = column(description, ts_abs, ts_share)
curdoc().add_root(layout)
