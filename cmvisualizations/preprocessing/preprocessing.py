"""
This script runs preprocessing on either a CProject folder or an elasticsearch-dump,
and produces dataframes as input for visualizations.
"""

import pandas as pd
import numpy as np
import os
from cmvisualizations import config

### functions for ingesting from elastic

factsfile = "facts.json"
metadatafile = "metadata.json"
rawdatapath = config.rawdatapath
cacheddatapath = config.cacheddatapath

def get_raw(filename):
    with open(filename) as infile:
        raw = infile.read()
        # the next line needs rewriting as soon as the zenodo-dump conforms to 'records'-format
        # [{k:v}, {k:v},...]
        rawfacts = pd.read_json('[%s]' % ','.join(raw.splitlines()), orient='records')
    return rawfacts


### functions for ingesting from CProject



### functions for preprocessing

def get_aspect(df):
    dicts = df["identifiers"].map(lambda x: x.get("contentmine"))
    return dicts.str.extract('([a-z]+)')

def clean(df):
    for col in df.columns:
        if type(df.head(1)[col][0]) == list:
            if len(df.head(1)[col][0]) == 1:
                notnull = df[df[col].notnull()]
                df[col] = notnull[col].map(lambda x: x[0])

def preprocess():
    rawfacts = get_raw(os.path.join(rawdatapath, factsfile))
    rawmetadata = get_raw(os.path.join(rawdatapath, metadatafile))
    parsed_facts = rawfacts.join(pd.DataFrame(rawfacts["_source"].to_dict()).T).drop("_source", axis=1)
    parsed_metadata = rawmetadata.join(pd.DataFrame(rawmetadata["_source"].to_dict()).T).drop("_source", axis=1)
    clean(parsed_facts)
    clean(parsed_metadata)
    df = pd.merge(parsed_facts, parsed_metadata, how="inner", on="cprojectID", suffixes=('_fact', '_meta'))
    df["sourcedict"] = get_aspect(df)
    df["term"] = df["term"].map(str.lower)
    return df

def get_preprocessed_df():
    try:
        df = pd.read_pickle(os.path.join(cacheddatapath, "preprocessed_df.pkl"))
    except:
        df = preprocess()
        df.to_pickle(os.path.join(cacheddatapath, "preprocessed_df.pkl"))
    return df


## functions to extract features

def count_occurrences(df):
    # replace pmcid by doi ideally
    groups = df[["pmcid", "term"]].groupby("term").groups
    return groups

def get_coocc_pivot(df):
    coocc_raw = df[["cprojectID", "term", "sourcedict"]]
    coocc_pivot = coocc_raw.pivot_table(index=["sourcedict", 'term'], columns='cprojectID', aggfunc=len)
    return coocc_pivot

def count_cooccurrences(df):
    coocc_pivot = get_coocc_pivot(df)
    labels = coocc_pivot.index
    M = np.matrix(coocc_pivot.fillna(0))
    C = np.dot(M, M.T)
    coocc_features = pd.DataFrame(data=C, index=labels, columns=labels)
    return coocc_features

def get_coocc_features():
    try:
        coocc_features = pd.read_pickle(os.path.join(cacheddatapath, "coocc_features.pkl"))
    except:
        df = get_preprocessed_df()
        coocc_features = count_cooccurrences(df)
        coocc_features.to_pickle(os.path.join(cacheddatapath, "coocc_features.pkl"))
    return coocc_features

def get_timeseries_pivot(df):
    ts_raw = df[["firstPublicationDate", "term", "sourcedict"]]
    ts_pivot = ts_raw.pivot_table(index='firstPublicationDate', columns=["sourcedict", "term"], aggfunc=len)
    return ts_pivot

def make_timeseries(df):
    ts = get_timeseries_pivot(df)
    ts.index = pd.to_datetime(ts.index)
    return ts

def get_timeseries_features():
    try:
        ts_features = pd.read_pickle(os.path.join(cacheddatapath, "timeseries_features.pkl"))
    except:
        df = get_preprocessed_df()
        ts_features = make_timeseries(df)
        ts_features.to_pickle(os.path.join(cacheddatapath, "timeseries_features.pkl"))
    return ts_features

def make_distribution_features(df):
    dist_raw = df[["firstPublicationDate", "sourcedict"]]
    dist_features = dist_raw.pivot_table(index="firstPublicationDate", columns=["sourcedict"], aggfunc=len)
    return dist_features

def get_distribution_features():
    try:
        dist_features = pd.read_pickle(os.path.join(cacheddatapath, "dist_features.pkl"))
    except:
        df = get_preprocessed_df()
        dist_features = make_distribution_features(df)
        dist_features.to_pickle(os.path.join(cacheddatapath, "distribution_features.pkl"))
    return dist_features

def get_single_fact(df, fact):
    fact_df = df[df["term"] == fact]
    return fact_df

def get_facts_from_list(df, factlist):
    return pd.concat((get_single_fact(df, f) for f in factlist))


####

def ingest_elasticdump(path):
    pass

def ingest_cproject(path):
    pass
