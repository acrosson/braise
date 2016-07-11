import numpy as np
import re
from collections import defaultdict
import scipy.sparse as sp

class CountVectorizer(object):

    """Transforms documents into a vector space

    properties
    --------------
    feature_names : list_type
                    a list contains all tokens of the corpus
                    ie ['apple', 'boy', 'green']

    feature_idx_map : dict_type
                        maps words to the index within the feature_names list
                        ie {'apple': 0, 'boy': 1, 'green': 2}

    """

    def __init__(self):
        self.feature_names = []
        self.feature_idx_map = {}

    def _tokenize(self, doc):
        """Returns a tokenized document"""
        doc = doc.lower()
        doc = re.sub('[^a-z]+', ' ', doc)

        # Remove extra whitespace
        doc = ' '.join(doc.split())
        return doc.split()

    def _fit(self, tokens):
        """Maps tokens to feature_names list and feature_idx_map used for
        converions of vectors representations to words

        Used for both fit and partial fit

        """
        for token in tokens:
            if token not in self.feature_idx_map:
                self.feature_names.append(token)
                self.feature_idx_map[token] = len(self.feature_names) - 1

    def fit(self, docs):
        """Fits a list of documents by calling private _fit method"""
        tokenized_docs = [self._tokenize(doc) for doc in docs]
        for tokens in tokenized_docs:
            self._fit(tokens)

    def partial_fit(self, doc):
        """Fits a single document by calling private _fit method"""
        tokens = self._tokenize(doc)
        self._fit(tokens)

    def transform(self, docs):
        """Transforms a new document into a vector representation based on
        the bag of words stores in the feature_idx_map

        """
        v_output = []
        for doc in docs:
            vector = np.zeros(len(self.feature_names))
            tokens = self._tokenize(doc)

            for token in tokens:
                if token in self.feature_idx_map:
                    vector[self.feature_idx_map[token]] += 1
            v_output.append(vector)

        return np.array(v_output)

class TfidfTransformer(object):

    """Transforms document vectors into tf-idf

    properties
    -----------
    vectors : numpy_array_type
                an array of all vectors within the corpus

    """

    def __init__(self):
        self.vectors = np.array([])

    def _document_frequency(self):
        """Gets the document frequency for all words"""
        return np.diff(sp.csc_matrix(self.vectors, copy=False).indptr)

    def fit(self, vectors):
        """Fit the model using vectors"""
        self.vectors = vectors

    def partial_fit(self, vector):
        """A partial fit method used for adding additional vectors"""
        self.vectors = np.concatenate((self.vectors,
                                       [vector]),
                                       axis=0)

    def transform(self, vectors):
        """Transfrom a new vector into a tf-idf representation"""
        output = []
        for vector in vectors:
            n_samples = len(self.vectors)
            df = self._document_frequency()

            # perform idf smoothing
            df += 1
            n_samples += 1

            # add 1 to idf to eensure we don't get zeros
            idf = np.log(float(n_samples) / df) + 1.0

            tfidf = df * idf
            output.append(tfidf)
        return np.array(output)
