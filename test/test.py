

"""
Runs a few tests.
"""
import unittest
import os

from pycproject.readctree import CProject
from pycproject import convert2elasticdump as cp2ed

import pandas as pd
from cmvisualizations.preprocessing import preprocessing


rawfactspath = "testdata/facts20160601-05.json"
rawmetadatapath = "testdata/metadata20160601-05.json"

class testDataConsistency(unittest.TestCase):

# ingestion
    #def setUp(self):

    def test_facts_existence(self):
        expected_length = 146645
        self.assertEqual(len(preprocessing.get_raw(rawfactspath)), expected_length)

    def test_metadata_existence(self):
        expected_length = 2746
        self.assertEqual(len(preprocessing.get_raw(rawmetadatapath)), expected_length)

    def test_raw_columns(self):
        expected_columns = ['_id', '_index', '_score', '_source', '_type']
        columns = list(preprocessing.get_raw(rawfactspath).columns.values)
        self.assertCountEqual(columns, expected_columns, "facts columns unequal")
        columns = list(preprocessing.get_raw(rawmetadatapath).columns.values)
        self.assertCountEqual(columns, expected_columns, "metadata columns unequal")

    def test_parsed_header(self):
        expected_columns = ['_id_fact',
                             '_index_fact',
                             '_score_fact',
                             '_type_fact',
                             'cprojectID',
                             'documentID',
                             'identifiers',
                             'post',
                             'prefix',
                             'term',
                             '_id_meta',
                             '_index_meta',
                             '_score_meta',
                             '_type_meta',
                             'abstractText',
                             'affiliation',
                             'authorIdList',
                             'authorList',
                             'authorString',
                             'chemicalList',
                             'citedByCount',
                             'commentCorrectionList',
                             'dateOfCompletion',
                             'dateOfCreation',
                             'dateOfRevision',
                             'dbCrossReferenceList',
                             'doi',
                             'electronicPublicationDate',
                             'embargoDate',
                             'epmcAuthMan',
                             'firstPublicationDate',
                             'fullTextUrlList',
                             'grantsList',
                             'hasBook',
                             'hasDbCrossReferences',
                             'hasLabsLinks',
                             'hasPDF',
                             'hasReferences',
                             'hasSuppl',
                             'hasTMAccessionNumbers',
                             'hasTextMinedTerms',
                             'id',
                             'inEPMC',
                             'inPMC',
                             'investigatorList',
                             'isOpenAccess',
                             'journalInfo',
                             'keywordList',
                             'language',
                             'license',
                             'luceneScore',
                             'meshHeadingList',
                             'pageInfo',
                             'pmcid',
                             'pmid',
                             'pubModel',
                             'pubTypeList',
                             'pubYear',
                             'source',
                             'subsetList',
                             'title',
                             'tmAccessionTypeList',
                             'sourcedict']
        testdf = preprocessing.preprocess(rawfactspath, rawmetadatapath)
        columns = list(testdf.columns.values)
        self.assertCountEqual(columns, expected_columns, "parsed columns unequal")

    def test_parseddf_size(self):
        testdf = preprocessing.get_preprocessed_df()
        expected_length = 144066
        self.assertEqual(len(testdf), expected_length)

    def test_parseddf_dtypes(self):
        testdf = preprocessing.get_preprocessed_df()
        expected_dtypes = {pd.np.dtype('int64'): ['_score_fact', '_score_meta'],
                             pd.np.dtype('O'): ['_id_fact',
                              '_index_fact',
                              '_type_fact',
                              'cprojectID',
                              'documentID',
                              'identifiers',
                              'post',
                              'prefix',
                              'term',
                              '_id_meta',
                              '_index_meta',
                              '_type_meta',
                              'abstractText',
                              'affiliation',
                              'authorIdList',
                              'authorList',
                              'authorString',
                              'chemicalList',
                              'citedByCount',
                              'commentCorrectionList',
                              'dateOfCompletion',
                              'dateOfCreation',
                              'dateOfRevision',
                              'dbCrossReferenceList',
                              'doi',
                              'electronicPublicationDate',
                              'embargoDate',
                              'epmcAuthMan',
                              'firstPublicationDate',
                              'fullTextUrlList',
                              'grantsList',
                              'hasBook',
                              'hasDbCrossReferences',
                              'hasLabsLinks',
                              'hasPDF',
                              'hasReferences',
                              'hasSuppl',
                              'hasTMAccessionNumbers',
                              'hasTextMinedTerms',
                              'id',
                              'inEPMC',
                              'inPMC',
                              'investigatorList',
                              'isOpenAccess',
                              'journalInfo',
                              'keywordList',
                              'language',
                              'license',
                              'luceneScore',
                              'meshHeadingList',
                              'pageInfo',
                              'pmcid',
                              'pmid',
                              'pubModel',
                              'pubTypeList',
                              'pubYear',
                              'source',
                              'subsetList',
                              'title',
                              'tmAccessionTypeList',
                              'sourcedict']}
        dtypes = testdf.columns.to_series().groupby(testdf.dtypes).groups
        self.assertDictEqual(dtypes, expected_dtypes)

    @classmethod
    def tearDownClass(testDataConsistency):
        if os.path.isfile("preprocessed_df.pkl"):
            os.remove("preprocessed_df.pkl")

if __name__ == '__main__':
    unittest.main()
    cleanup()


# test preprocessing
# feature extraction
