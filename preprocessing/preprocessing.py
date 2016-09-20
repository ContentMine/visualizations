"""
This script runs preprocessing on either a CProject folder or an elasticsearch-dump,
and produces dataframes as input for visualizations.
"""

import pandas as pd
import numpy as np
import os
import pickle
import gzip, bz2
import itertools
import argparse

import config


def get_raw(filename):
    with open(filename) as infile:
        raw = infile.read()
        # the next line needs rewriting as soon as the zenodo-dump conforms to 'records'-format
        # [{k:v}, {k:v},...]
        rawfacts = pd.read_json('[%s]' % ','.join(raw.splitlines()), orient='records')
    return rawfacts


### functions for ingesting from CProject



### functions for preprocessing

def get_dictionary(df):
    dicts = df["identifiers"].map(lambda x: x.get("contentmine"))
    return dicts.str.extract('([a-z]+)')

def clean(df):
    for col in df.columns:
        if type(df.head(1)[col][0]) == list:
            if len(df.head(1)[col][0]) == 1:
                notnull = df[df[col].notnull()]
                df[col] = notnull[col].map(lambda x: x[0])

def preprocess(rawdatapath):
    rawfacts = get_raw(os.path.join(rawdatapath, "facts.json"))
    rawmetadata = get_raw(os.path.join(rawdatapath, "metadata.json"))
    parsed_facts = rawfacts.join(pd.DataFrame(rawfacts["_source"].to_dict()).T).drop("_source", axis=1)
    parsed_metadata = rawmetadata.join(pd.DataFrame(rawmetadata["_source"].to_dict()).T).drop("_source", axis=1)
    clean(parsed_facts)
    clean(parsed_metadata)
    df = pd.merge(parsed_facts, parsed_metadata, how="inner", on="cprojectID", suffixes=('_fact', '_meta'))
    df["sourcedict"] = get_dictionary(df)
    df["term"] = df["term"].map(str.lower)
    df.drop_duplicates("_id_fact", inplace=True)
    return df

def get_preprocessed_df(cacheddatapath, rawdatapath):
    try:
        with gzip.open(os.path.join(cacheddatapath, "preprocessed_df.pklz"), "rb") as infile:
            df = pickle.load(infile)
    except:
        df = preprocess(rawdatapath)
        with gzip.open(os.path.join(cacheddatapath, "preprocessed_df.pklz"), "wb") as outfile:
            pickle.dump(df, outfile, protocol=4)
    return df


## functions to extract features

def make_series(df, column):
    series = df[["firstPublicationDate", "sourcedict", column]]
    #series.index = pd.to_datetime(df["firstPublicationDate"])
    return series

def get_series(cacheddatapath, rawdatapath, column):
    try:
        with gzip.open(os.path.join(cacheddatapath, column+"_series.pklz"), "rb") as infile:
            series = pickle.load(infile)
    except:
        df = get_preprocessed_df(cacheddatapath, rawdatapath)
        series = make_series(df, column)
        with gzip.open(os.path.join(cacheddatapath, column+"_series.pklz"), "wb") as outfile:
            pickle.dump(series, outfile, protocol=4)
    return series


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

def get_coocc_features(cacheddatapath, rawdatapath):
    try:
        with bz2.open(os.path.join(cacheddatapath, "coocc_features.pklz2"), "r") as infile:
            coocc_features = pickle.load(infile)
    except:
        df = get_preprocessed_df(cacheddatapath, rawdatapath)
        coocc_features = count_cooccurrences(df)
        with bz2.BZ2File(os.path.join(cacheddatapath, "coocc_features.pklz2"), "w") as outfile:
            pickle.dump(coocc_features, outfile, protocol=4)
    return coocc_features

def make_subset(coocc_features, x_axis, y_axis):
    logsource = np.log(coocc_features.ix[x_axis][y_axis]+1)
    x_sorted = logsource.ix[logsource.sum(axis=1).sort_values(ascending=False).index]
    y_sorted = x_sorted.T.ix[x_sorted.T.sum(axis=1).sort_values(ascending=False).index]
    logsource = y_sorted.T.ix[:25, :25]
    n_cols = len(logsource.columns)
    n_rows = len(logsource.index)
    df = pd.DataFrame()
    df["x"] = list(itertools.chain.from_iterable(list(itertools.repeat(i, times=n_cols)) for i in logsource.index))
    df["y"] = list(itertools.chain.from_iterable(list(itertools.repeat(logsource.stack().index.levels[1].values, times=n_rows))))
    df["counts"] = logsource.stack().values
    df["raw"] = df["counts"].map(np.exp)-1
    df.sort_values("counts", ascending=False, inplace=True)

    new_axis_factors = logsource.index.values.tolist()

    return df, new_axis_factors, new_axis_factors

def prepare_facts(cacheddatapath, rawdatapath):
    coocc_features = get_coocc_features(cacheddatapath, rawdatapath)
    dictionaries = sorted(coocc_features.index.levels[0])
    factsets = {}
    for dictionary in dictionaries:
        subset = make_subset(coocc_features, dictionary, dictionary)
        factsets[(dictionary, dictionary)] = subset
    return factsets

def get_coocc_factsets(cacheddatapath, rawdatapath):
    try:
        with gzip.open(os.path.join(cacheddatapath, "coocc_factsets.pklz"), "rb") as infile:
            coocc_factsets = pickle.load(infile)
    except:
        coocc_factsets = prepare_facts(cacheddatapath, rawdatapath)
        with gzip.open(os.path.join(cacheddatapath, "coocc_factsets.pklz"), "wb") as outfile:
            pickle.dump(coocc_factsets, outfile, protocol=4)
    return coocc_factsets


def get_timeseries_pivot(df):
    ts_raw = df[["firstPublicationDate", "term", "sourcedict"]]
    ts_pivot = ts_raw.pivot_table(index='firstPublicationDate', columns=["sourcedict", "term"], aggfunc=len)
    return ts_pivot

def make_timeseries(df):
    ts = get_timeseries_pivot(df)
    ts.index = pd.to_datetime(ts.index)
    return ts

def get_timeseries_features(cacheddatapath, rawdatapath):
    try:
        with gzip.open(os.path.join(cacheddatapath, "timeseries_features.pklz"), "rb") as infile:
            ts_features = pickle.load(infile)
    except:
        df = get_preprocessed_df(cacheddatapath, rawdatapath)
        ts_features = make_timeseries(df)
        with gzip.open(os.path.join(cacheddatapath, "timeseries_features.pklz"), "wb") as outfile:
            pickle.dump(ts_features, outfile, protocol=4)
    return ts_features

def make_distribution_features(df):
    dist_raw = df[["firstPublicationDate", "sourcedict"]]
    dist_features = dist_raw.pivot_table(index="firstPublicationDate", columns=["sourcedict"], aggfunc=len)
    return dist_features

def get_distribution_features(cacheddatapath, rawdatapath):
    try:
        with gzip.open(os.path.join(cacheddatapath, "dist_features.pklz"), "rb") as infile:
            dist_features = pickle.load(infile)
    except:
        df = get_preprocessed_df(cacheddatapath, rawdatapath)
        dist_features = make_distribution_features(df)
        with gzip.open(os.path.join(cacheddatapath, "dist_features.pklz"), "wb") as outfile:
            pickle.dump(dist_features, outfile, protocol=4)
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

#####

def main(args):

    if args.raw:
        rawdatapath = args.raw
    else:
        rawdatapath = config.rawdatapath

    if args.cache:
        cacheddatapath = args.cache
    else:
        cacheddatapath = config.cacheddatapath

    get_preprocessed_df(cacheddatapath, rawdatapath)
    get_series(cacheddatapath, rawdatapath, "term")
    get_coocc_features(cacheddatapath, rawdatapath)
    get_distribution_features(cacheddatapath, rawdatapath)
    get_timeseries_features(cacheddatapath, rawdatapath)
    get_coocc_factsets(cacheddatapath, rawdatapath)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='ingest and preprocess contentmine facts from elasticsearch dumps and CProjects')
    parser.add_argument('--raw', dest='raw', help='relative or absolute path of the raw data folder', required=True)
    parser.add_argument('--cache', dest='cache', help='relative or absolute path of the cached data folder', required=True)
    parser.add_argument('--results', dest='results', help='relative or absolute path of the results folder')
    parser.add_argument('--elastic', dest='elastic', help='flag if input is elastic-dump', action="store_true")
    parser.add_argument('--cproject', dest='cproject', help='flag if input is cproject', action="store_true")
    args = parser.parse_args()
    main(args)
