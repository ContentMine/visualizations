# main.py
import os

from math import pi
import numpy as np
import pandas as pd
import glob

from bokeh.layouts import column, row
from bokeh.plotting import Figure, show
from bokeh.embed import standalone_html_page_for_models
from bokeh.models import ColumnDataSource, HoverTool, HBox, VBox
from bokeh.models.widgets import Slider, Select, TextInput, RadioGroup, Paragraph, Div
from bokeh.io import curdoc, save
from bokeh.charts import HeatMap, bins, output_file, vplot, TimeSeries
from bokeh.models import FixedTicker, SingleIntervalTicker, ColumnDataSource, DataRange1d
from bokeh.layouts import widgetbox
from bokeh.layouts import gridplot
import bokeh.palettes as palettes
from bokeh.resources import INLINE, CDN

from itertools import chain, repeat

from cmvisualizations.preprocessing import preprocessing
from cmvisualizations import config


ts = preprocessing.get_timeseries_features()
facets = sorted(ts.columns.levels[0])
resources = INLINE

def get_selection(ts, facetvalue, top_n=5, frequency="D", trending=False):
    if trending:
        ts = ts.diff()/ts*100
        ts = ts.cumsum()
    selection = ts.groupby(pd.TimeGrouper(freq=frequency)) \
                    .sum()[facetvalue] \
                    .sum().sort_values(ascending=False)[:top_n] \
                    .index
    selected = ts[facetvalue][selection]
    return selected

colors = palettes.Paired12

def make_plots(selected, header):
    plots = []
    plots.append(Paragraph(text=header, width=200, height=50))
    for l in selected:
        source = ColumnDataSource(dict(date=selected.index, y=selected[l]))
        height = 50

        fig = Figure(title=None, toolbar_location=None,
                   x_axis_type="datetime",
                   width=200, height=height)
        fig.xaxis.visible = False
        fig.yaxis.visible = False
        fig.xgrid.visible = False
        fig.ygrid.visible = False
        fig.min_border_left = 3
        fig.min_border_right = 3
        fig.min_border_top = 3
        fig.min_border_bottom = 3
        fig.xaxis.major_label_text_font_size = "0pt"
        fig.yaxis.major_label_text_font_size = "0pt"
        fig.xaxis.major_tick_line_color = None
        fig.yaxis.major_tick_line_color = None
        fig.xaxis.minor_tick_line_color = None
        fig.yaxis.minor_tick_line_color = None
        fig.background_fill_color = "whitesmoke"
        fig.line(x='date', y="y", source=source)

        text = """<div align="left" style="vertical-align: middle">%d: %s</div>""" %(selected[l].sum(), l)
        d = Div(text=text, width=150, height=25)

        plots.append(row(fig,d))
    return column(plots)

def arrange_facets(facets):
    arrangement = []
    for facet in facets:
        absolutes = make_plots(get_selection(ts, facet), "Top "+facet)
        trendings = make_plots(get_selection(ts, facet, trending=True), "Trending "+facet)
        arrangement.append(row(absolutes, trendings))
    return arrangement

arrangement = arrange_facets(facets)
layout = gridplot(arrangement, ncols=4)

# session = push_session(curdoc())
# script = autoload_server(plot, session_id=session.id)

show(layout)
output_file(os.path.join(config.resultspath, "static_timeseries_trending.html"), title="Static timeseries", mode='inline')
save(obj=layout, filename=os.path.join(config.resultspath, 'static_timeseries_trending.html'), resources=INLINE)
