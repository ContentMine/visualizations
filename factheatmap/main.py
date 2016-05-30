# factheatmap.py

from os.path import dirname, join

from math import pi
import numpy as np
import pandas as pd

from bokeh.plotting import figure, show, Figure
from bokeh.models import ColumnDataSource, HoverTool, HBox, VBoxForm, VBox
from bokeh.models.widgets import Slider, Select, TextInput
from bokeh.io import curdoc
from bokeh.charts import HeatMap, bins, output_file, vplot
from bokeh.models import FixedTicker, SingleIntervalTicker
from bokeh.models.ranges import FactorRange
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
pluginoptions = ["binomial", "genus"]

# Create Input controls
top_n = Slider(title="Number of top-n items to display", value=20, start=5, end=50, step=5)
x_axis = Select(title="X Axis", options=sorted(pluginoptions), value="binomial")
y_axis = Select(title="Y Axis", options=sorted(pluginoptions), value="genus")


x = []
x_optionlist = []
y = []
y_optionlist = []
counts = []
for x_option in pluginoptions:
    for y_option in pluginoptions:
        logsource = select_cooccurrences(x_option, y_option)
        for xx in logsource.columns:
            for yy in logsource.index:
                x.append(xx)
                x_optionlist.append(x_option)
                y.append(yy)
                y_optionlist.append(y_option)
                counts.append(logsource[xx][yy])

df2 = pd.DataFrame()
df2["x"] = x
df2["x_option"] = x_optionlist
df2["y"] = y
df2["y_option"] = y_optionlist
df2["counts"] = counts
bins = np.linspace(df2.counts.min(), df2.counts.max(), 10) # bin labels must be one more than len(colorpalette)
color = pd.cut(df2.counts, bins, labels = list(reversed(palettes.Blues9)), include_lowest=True)
df2["color"] = color


def select_facts():
    selected = df2[
        (df2.x_option.isin([x_axis.value]) &
         df2.y_option.isin([y_axis.value]))
    ]
    return selected

def update(attrname, old, new):
    selected = select_facts()

    p.xaxis.axis_label = x_axis.value
    p.yaxis.axis_label = y_axis.value
    p.title = "Top %d fact co-occurrences selected" % top_n.value
    src = ColumnDataSource(dict(
        x=selected["x"].astype(object),
        y=selected["y"].astype(object),
        color=selected["color"].astype(object)
    ))
    source.data.update(src.data)
    p.x_range.update(factors=list(set(source.data.get("x"))))
    p.y_range.update(factors=list(set(source.data.get("y"))))

selected = select_facts()
source = ColumnDataSource(data=dict(x=[], y=[], color=[]))
source.data.update(ColumnDataSource(dict(
    x=selected["x"].astype(object),
    y=selected["y"].astype(object),
    color=selected["color"].astype(object)
    )).data)

p = Figure(plot_height=900, plot_width=900, title="", toolbar_location=None,
           x_range=list(set(source.data.get("x"))), y_range=list(set(source.data.get("y"))))
p.rect(x="x", y="y", source=source, color="color", width=1, height=1)
p.xaxis.major_label_orientation = pi/4
p.yaxis.major_label_orientation = pi/4

controls = [top_n, x_axis, y_axis]
for control in controls:
    control.on_change('value', update)

inputs = HBox(VBoxForm(*controls), width=300)

update(None, None, None) # initial load of the data

layout = HBox(inputs, p)
curdoc().add_root(layout)
