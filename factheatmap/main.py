# factheatmap.py

from os.path import dirname, join

from math import pi
import numpy as np
import pandas as pd

from bokeh.plotting import figure, show
from bokeh.models import ColumnDataSource, HoverTool, HBox, VBoxForm
from bokeh.models.widgets import Slider, Select, TextInput
from bokeh.io import curdoc
from bokeh.charts import HeatMap, bins, output_file, vplot
from bokeh.models import FixedTicker, SingleIntervalTicker
import bokeh.palettes as palettes

from pycproject.readctree import CProject
from collections import Counter
from itertools import chain

projectpath = "/home/chris/projects/ContentMine/"
projectname = "aedes"
raw = CProject(projectpath, projectname)

def get_data(raw):
    """
    From CProject to pandas-dataframe.
    """
    frames = []
    for ctree in raw.get_ctrees():
        data = {}
        for plugin, results in ctree.results.items():
            for type_, facts in results.items():
                data[type_] = {}
                if type_ in ["human", "dnaprimer"]:
                    for count, value in Counter([fact.get("exact") for fact in facts]).most_common():
                        #print(count, value)
                        data[type_][count] = value
                #print(type_, paper.ID, Counter([fact.get("match") for fact in facts]))
                #df.loc[('bar','two'),'A'] = 9999
                else:
                    for count, value in Counter([fact.get("match") for fact in facts]).most_common():
                        #print(count, value)
                        data[type_][count] = value
        row = pd.DataFrame(reform(data), [ctree.ID])
        frames.append(row)
    df = pd.concat(frames)
    return df

def get_metadata(raw):
    """
    From CProject to pandas-dataframe,
    metadata only.
    """
    frames = []
    for ctree in raw.get_ctrees():
        row = pd.DataFrame([ctree.first_publication_date], [ctree.ID])
        frames.append(row)
    df = pd.concat(frames)
    return df

def reform(data):
    """
    from http://stackoverflow.com/questions/24988131/nested-dictionary-to-multiindex-dataframe-where-dictionary-keys-are-column-label
    Transform a nested dictionary to a multiindex dataframe.
    """
    return {(outerKey, innerKey): values for outerKey, innerDict in data.items() for innerKey, values in innerDict.items()}

def get_cooccurrences(df):
    df_asint = df.fillna(0).astype(int)
    coocc = df_asint.T.dot(df_asint)
    return coocc

def select_cooccurrences(x_option, y_option):
    coocc = get_cooccurrences(df)
    x_selection = coocc.loc[x_option][y_option].sum(1).sort_values(ascending=False)[:top_n.value].index.values
    y_selection = coocc.loc[x_option][y_option].sum(0).sort_values(ascending=False)[:top_n.value].index.values
    rawsource = coocc[x_option][x_selection].loc[y_option].T[y_selection]
    logsource = pd.np.log(rawsource+1)
    return logsource


df = get_data(raw)
meta = get_metadata(raw)
pluginoptions = sorted(df.columns.levels[0])

# create input controls
top_n = Slider(title="Number of top-n items to display", value=20, start=5, end=50, step=5)

def create_heatmap(x_option, y_option):

    logsource = select_cooccurrences(x_option, y_option)
    x = []
    y = []
    counts = []
    for xx in logsource.columns:
        for yy in logsource.index:
            value = logsource[xx][yy]
            x.append(xx)
            y.append(yy)
            counts.append(value)
    source = pd.DataFrame()
    source["x"] = x
    source["y"] = y
    source["counts"] = counts
    bins = np.linspace(source.counts.min(), source.counts.max(), 10) # bin labels must be one more than len(colorpalette)
    colors = pd.cut(source.counts, bins, labels = list(reversed(palettes.Blues9)), include_lowest=True)
    source["colors"] = colors

    width = len(logsource.columns) * 30
    height = len(logsource.index) * 30

    # axis tick categorical tickers
    xfactors = logsource.columns.tolist()
    yfactors = logsource.index.tolist()

    p = figure(plot_height=height, plot_width=width, title="", x_range=xfactors, y_range=yfactors)
    p.title = "Top %d %s-%s co-occurrences selected" %(top_n.value, x_option, y_option)

    for color in set(colors):
        x = source[source["colors"]==color]["x"].values.tolist()
        y = source[source["colors"]==color]["y"].values.tolist()
        colors = list(source[source["colors"]==color]["colors"])
        #p.quad(top=[i+1 for i in x], bottom=x, left=y, right=[i+1 for i in y], color=color)
        #p.rect(x=x, y=y, color=color)
        p.rect(x, y, color=colors, width=1, height=1)

    p.xaxis.major_label_orientation = pi/4
    p.yaxis.major_label_orientation = pi/4

    return p


hboxes = []
for xo in ["binomial", "genus", "human", "dnaprimer"]:
    row = []
    for yo in ["binomial", "genus", "human", "dnaprimer"]:
        row.append(create_heatmap(xo, yo))
    hboxes.append(HBox(*row))

layout = VBox(*hboxes)
curdoc().add_root(layout)
