# main.py
import numpy as np
import pandas as pd


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

import config
import pickle
import gzip

with gzip.open("../data/timeseries_features.pklz", "rb") as infile:
    ts = pickle.load(infile)

dictionaries = sorted(ts.columns.levels[0])
resources = INLINE
colors=palettes.Paired10

def get_dataset(df, dictvalue, relative):
    rel = (df.diff()/df*100).cumsum()
    if relative:
        selection = rel.sum()[dictvalue].sort_values(ascending=False).index
        # check with tail(5) of df; or second half/third/quarter of df only
    else:
        selection = df.sum()[dictvalue].sort_values(ascending=False).index
    selected = df[dictvalue][selection].fillna(0)
    return selected

def prepare_facts(dictionaries):
    factsets = {}
    for dictionary in dictionaries:
        absolutes = get_dataset(ts, dictionary, False)
        trendings = get_dataset(ts, dictionary, True)
        factsets[dictionary] = (absolutes, trendings)
    return factsets

factsets = prepare_facts(dictionaries)


def get_subset(dictionary):
    subset = factsets.get(dictionary)
    return subset

def update(attrname, old, new):
    subset = get_subset(dictchooser.value)
    new_absolute_source = subset[0] \
                                        .ix[:, :top_n.value] \
                                        .groupby(pd.TimeGrouper(freq=timegroupoptionsmapper[timegroup.active])) \
                                        .sum().fillna(0)
    new_relative_source = subset[1] \
                                        .ix[:, :top_n.value] \
                                        .groupby(pd.TimeGrouper(freq=timegroupoptionsmapper[timegroup.active])) \
                                        .sum().fillna(0)

    for old, new in zip(abs_arrangement, new_absolute_source.columns.tolist()):
        old.title.text = new
    for old, new in zip(rel_arrangement, new_relative_source.columns.tolist()):
        old.title.text = new

    new_abs_sources = [ColumnDataSource(dict(date=new_absolute_source.index,
                                             y=new_absolute_source[l]))
                                                for l in new_absolute_source.columns.tolist()]
    new_rel_sources = [ColumnDataSource(dict(date=new_relative_source.index,
                                             y=new_relative_source[l]))
                                                for l in new_relative_source.columns.tolist()]
    for old, new in zip(abs_sources, new_abs_sources):
        old.data.update(new.data)
    for old, new in zip(rel_sources, new_rel_sources):
        old.data.update(new.data)

    new_abs_point_sources = [ColumnDataSource(dict(date=[new_absolute_source[l].idxmax()],
                                               y=[new_absolute_source[l].max()],
                                               text=[str(int(new_absolute_source[l].max()))]
                                               )
                                          )
                                          for l in new_absolute_source.columns.tolist()]
    new_rel_point_sources = [ColumnDataSource(dict(date=[new_relative_source[l].idxmax()],
                                               y=[new_relative_source[l].max()],
                                               text=[str(int(new_relative_source[l].max()))]
                                               )
                                          )
                                          for l in new_relative_source.columns.tolist()]
    for old, new in zip(abs_point_sources, new_abs_point_sources):
        old.data.update(new.data)
    for old, new in zip(rel_point_sources, new_rel_point_sources):
        old.data.update(new.data)

# Create Input controls
timegroupoptionsmapper = {0:"A", 1:"M", 2:"D"}
trendingoptionsmapper = {0:False, 1:True}
timegroupoptions = ["Year", "Month", "Day"]

top_n = Slider(title="Number of top-n items to display", value=10, start=1, end=10, step=1)
dictchooser = Select(title="dictionaries", options=dictionaries, value=dictionaries[-2])
timegroup = RadioGroup(labels=timegroupoptions, active=0)
trending_chooser = RadioGroup(labels=["absolute counts", "period-to-period change"], active=0)

initial_subset = get_subset(dictchooser.value)
abs_sources = [ColumnDataSource(dict(date=initial_subset[0].index, y=initial_subset[0][l])) for l in initial_subset[0].columns.tolist()[:top_n.value]]
rel_sources = [ColumnDataSource(dict(date=initial_subset[1].index, y=initial_subset[1][l])) for l in initial_subset[1].columns.tolist()[:top_n.value]]
abs_point_sources = [ColumnDataSource(dict(date=[initial_subset[0][l].idxmax()],
                                           y=[initial_subset[0][l].max()],
                                           text=[str(int(initial_subset[0][l].max()))]
                                           )
                                      )
                                      for l in initial_subset[0].columns.tolist()[:top_n.value]]
rel_point_sources = [ColumnDataSource(dict(date=[initial_subset[1][l].idxmax()],
                                           y=[initial_subset[1][l].max()],
                                           text=[str(int(initial_subset[0][l].max()))]
                                           )
                                      )
                                      for l in initial_subset[1].columns.tolist()[:top_n.value]]

def make_plots(linesources, pointsources):
    plots = []
    i=0
    for linesource, pointsource in zip(linesources, pointsources):
        fig = Figure(title=None, toolbar_location=None, tools=[],
                   x_axis_type="datetime",
                   width=300, height=70)

        fig.xaxis.visible = False
        if i in [0, 9] :
            fig.xaxis.visible = True
            fig.height = 90
        fig.yaxis.visible = False
        fig.xgrid.visible = True
        fig.ygrid.visible = False
        fig.min_border_left = 10
        fig.min_border_right = 10
        fig.min_border_top = 5
        fig.min_border_bottom = 5
        if not i in [0, 9]:
            fig.xaxis.major_label_text_font_size = "0pt"
        #fig.yaxis.major_label_text_font_size = "0pt"
        fig.xaxis.major_tick_line_color = None
        fig.yaxis.major_tick_line_color = None
        fig.xaxis.minor_tick_line_color = None
        fig.yaxis.minor_tick_line_color = None
        fig.background_fill_color = "whitesmoke"

        fig.line(x='date', y="y", source=linesource)
        fig.circle(x='date', y='y', size=5, source=pointsource)
        fig.text(x='date', y='y', text='text', x_offset=5, y_offset=10, text_font_size='7pt', source=pointsource)

        fig.title.align = 'left'
        fig.title.text_font_style = 'normal'

        plots.append(fig)
        i+=1
    return plots

abs_arrangement = make_plots(abs_sources, abs_point_sources)
rel_arrangement = make_plots(rel_sources, rel_point_sources)

dictchooser.on_change("value", update)
timegroup.on_change('active', update)

inputs = row(dictchooser, timegroup)

update(None, None, None) # initial load of the data

### LAYOUT

layout = column(inputs, row(column(abs_arrangement), column(rel_arrangement)))
curdoc().add_root(layout)
curdoc.title = "Exploring most frequent and uptrending facts"
