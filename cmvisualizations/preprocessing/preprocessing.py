"""
This script runs preprocessing on either a CProject folder or an elasticsearch-dump,
and produces dataframes as input for visualizations.
"""

import argparse
import pandas as pd
import numpy as np
from hashlib import md5
import os

parser = argparse.ArgumentParser(description='ingest and preprocess contentmine facts from elasticsearch dumps and CProjects')
parser.add_argument('--raw', dest='raw', help='relative or absolute path of the raw data folder')
parser.add_argument('--elastic', dest='elastic', help='flag if input is elastic-dump', action="store_true")
parser.add_argument('--cproject', dest='cproject', help='flag if input is cproject', action="store_true")
args = parser.parse_args()

### functions for ingesting from elastic


factsfile = "facts20160601-05.json"
metadatafile = "metadata20160601-05.json"
datapath = os.path.join(os.getcwd(),"../test/testdata/")
fname = md5(factsfile.encode("utf-8")+metadatafile.encode("utf-8")).hexdigest()

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
    rawfacts = get_raw(os.path.join(datapath, factsfile))
    rawmetadata = get_raw(os.path.join(datapath, metadatafile))
    parsed_facts = rawfacts.join(pd.DataFrame(rawfacts["_source"].to_dict()).T).drop("_source", axis=1)
    parsed_metadata = rawmetadata.join(pd.DataFrame(rawmetadata["_source"].to_dict()).T).drop("_source", axis=1)
    clean(parsed_facts)
    clean(parsed_metadata)
    df = pd.merge(parsed_facts, parsed_metadata, how="inner", on="cprojectID", suffixes=('_fact', '_meta'))
    df["sourcedict"] = get_aspect(df)
    df.to_pickle(fname+"preprocessed_df.pkl")
    return df

def get_preprocessed_df():
    try:
        df = pd.read_pickle(fname+"preprocessed_df.pkl")
    except:
        df = preprocess()
    return df


## functions to extract features

def make_coocc_pivot():
    df = get_preprocessed_df()
    coocc_raw = df[["cprojectID", "term", "sourcedict"]]
    coocc_pivot = coocc_raw.pivot_table(index=["sourcedict", 'term'], columns='cprojectID', aggfunc=len)
    return coocc_pivot

def get_coocc_pivot():
    coocc_pivot = make_coocc_pivot()
    return coocc_pivot

def make_cooccurrences():
    df = get_coocc_pivot()
    labels = df.index
    M = np.matrix(df.fillna(0))
    C = np.dot(M, M.T)
    coocc = pd.DataFrame(data=C, index=labels, columns=labels)
    coocc.to_pickle(fname+"coocc_features.pkl")
    return coocc

def get_coocc_features():
    try:
        coocc_features = pd.read_pickle(fname+"coocc_features.pkl")
    except:
        coocc_features = make_cooccurrences()
    return coocc_features

def ingest_elasticdump(path):
    pass

def ingest_cproject(path):
    pass

def main(args):
    if args.elastic:
        ingest_elasticdump(args.raw)
    if args.cproject:
        ingest_cproject(args.raw)

if __name__ == '__main__':
    main(args)
