# factheatmap.py

import os

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from bokeh.plotting import Figure, show
from bokeh.models import ColumnDataSource, HoverTool, HBox, VBox, VBoxForm
from bokeh.models.widgets import Slider, Select, TextInput
from bokeh.io import curdoc, output_notebook
from bokeh.charts import HeatMap, bins, output_file, vplot
from bokeh.models import FixedTicker, SingleIntervalTicker
import bokeh.palettes as palettes

import itertools

projectpath = "/home/chris/projects/ContentMine/"
projectname = "api-demo"

facts_filename = os.path.join(projectpath, projectname, "facts20160601-05.json")
metadata_filename = os.path.join(projectpath, projectname, "metadata20160601-05.json")


def get_rawfacts(facts_filename):
    with open(facts_filename) as infile:
        raw = infile.read()
        # the next line needs rewriting as soon as the zenodo-dump conforms to 'records'-format
        # [{k:v}, {k:v},...]
        rawfacts = pd.read_json('[%s]' % ','.join(raw.splitlines()), orient='records')
    return rawfacts

def get_rawmetadata(metadata_filename):
    with open(metadata_filename) as infile:
        raw = infile.read()
        rawmetadata = pd.read_json('[%s]' % ','.join(raw.splitlines()), orient='records')
    return raw_metadata

def clean(df):
    for col in df.columns:
        if type(df.head(1)[col][0]) == list:
            if len(df.head(1)[col][0]) == 1:
                notnull = df[df[col].notnull()]
                df[col] = notnull[col].map(lambda x: x[0])

def get_aspect(df):
    dicts = df["identifiers"].map(lambda x: x.get("contentmine"))
    return dicts.str.extract('([a-z]+)')

def preprocess():
    rawfacts = get_rawfacts()
    rawmetadata = get_rawmetadata()
    parsed_facts = rawfacts.join(pd.DataFrame(rawfacts["_source"].to_dict()).T).drop("_source", axis=1)
    parsed_metadata = rawmetadata.join(pd.DataFrame(rawmetadata["_source"].to_dict()).T).drop("_source", axis=1)
    clean(parsed_facts)
    clean(parsed_metadata)
    df = pd.merge(parsed_facts, parsed_metadata, how="inner", on="cprojectID", suffixes=('_fact', '_meta'))
    df["sourcedict"] = get_aspect(df)
    df.to_pickle("preprocessed_df.pkl")
    return df

def get_preprocessed_df():
    try:
        df = pd.read_pickle("preprocessed_df.pkl")
    except:
        df = preprocess()
    return df

def make_coocc_pivot():
    df = get_preprocessed_df()
    coocc_raw = df[["cprojectID", "term", "sourcedict"]]
    coocc_pivot = coocc_raw.pivot_table(index=["sourcedict", 'term'], columns='cprojectID', aggfunc=len)
    coocc_pivot.to_pickle("coocc_pivot.pkl")
    return coocc_pivot

def get_coocc_pivot():
    try:
        coocc_pivot = pd.read_pickle("coocc_pivot.pkl")
    except:
        coocc_pivot = make_coocc_pivot()
    return coocc_pivot

def make_cooccurrences():
    df = get_coocc_pivot()
    labels = df.index
    M = np.matrix(df.fillna(0))
    C = np.dot(M, M.T)
    coocc = pd.DataFrame(data=C, index=labels, columns=labels)
    coocc.to_pickle("coocc_features.pkl")
    return coocc

def get_coocc_features():
    try:
        coocc_features = pd.read_pickle("coocc_features.pkl")
    except:
        coocc_features = make_cooccurrences()
    return coocc_features

coocc_features = get_coocc_features()

# Create Input controls
pluginoptions = sorted(coocc_features.index.levels[0])
top_n = Slider(title="Number of top-n items to display", value=20, start=5, end=50, step=5)
x_axis = Select(title="X Axis", options=sorted(pluginoptions), value=pluginoptions[0])
y_axis = Select(title="Y Axis", options=sorted(pluginoptions), value=pluginoptions[0])


def select_facts(coocc_features):
    logsource = np.log(coocc_features.ix[x_axis.value][y_axis.value]+1)

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

def update(attrname, old, new):
    new_selected = select_facts(coocc_features)

    p.xaxis.axis_label = x_axis.value
    p.yaxis.axis_label = y_axis.value
    p.title = "Top %d fact co-occurrences selected" % top_n.value
    src = ColumnDataSource(dict(
        x=new_selected["x"].astype(object),
        y=new_selected["y"].astype(object),
        color=new_selected["color"].astype(object)
    ))
    source.data.update(src.data)
    p.x_range.update(factors=list(set(source.data.get("x"))))
    p.y_range.update(factors=list(set(source.data.get("y"))))

selected = select_facts(coocc_features)
source = ColumnDataSource(data=dict(x=[], y=[], color=[]))
source.data.update(ColumnDataSource(dict(
    x=selected["x"].astype(object),
    y=selected["y"].astype(object),
    color=selected["color"].astype(object)
    )).data)

p = Figure(plot_height=900, plot_width=900, title="", toolbar_location=None,
           x_range=list(set(source.data.get("x"))), y_range=list(set(source.data.get("y"))))
p.rect(x="x", y="y", source=source, color="color", width=1, height=1)
p.xaxis.major_label_orientation = np.pi/4
p.yaxis.major_label_orientation = np.pi/4

controls = [top_n, x_axis, y_axis]
for control in controls:
    control.on_change('value', update)

inputs = HBox(VBoxForm(*controls), width=300)

update(None, None, None) # initial load of the data

layout = HBox(inputs, p)
curdoc().add_root(layout)
