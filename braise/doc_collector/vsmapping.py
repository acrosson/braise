from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
import redis
import cPickle as pickle
import config
import utils

class VSMapping(object):

    """VSMapping

    The VSMapping stores the count vector and tf-idf transformer used to
    transform document into vector spaces. All info is persisted to memory
    using a redis database.

    """

    def __init__(self):
        """Initialization"""
        self.count_vect = CountVectorizer()
        self.tfidf = TfidfTransformer(norm="l2")
        self.feature_names = []

        # Initialize redis connection
        self.r = redis.StrictRedis(host=config.REDIS_HOST,
                                   port=config.REDIS_PORT,
                                   db=config.REDIS_DB)

    def partial_fit(self):
        """Partially fit the count_vect and tfidf transformer"""
        # TODO : Complete this partial fit
        return

    def batch_fit(self, data):
        """Batch fit the count_vect and tfidf transformer

        inputs
        -------------
        data : array_type
                an array of documents stored as strings

        """
        # Fit and transform into frequency term matrix
        # and persist freq_term_matrix to memory
        self.count_vect.fit(data)
        freq_term_matrix = self.count_vect.transform(data)
        self.store_val('count_vect', pickle.dumps(self.count_vect))

        # Fit the tf-idf model with the matrix
        self.tfidf.fit(freq_term_matrix)
        self.store_val('tfidf', pickle.dumps(self.tfidf))

        # Store the feature names for latter use
        self.feature_names = self.count_vect.get_feature_names()
        self.store_val('feature_names', self.feature_names)

    def transform(self, doc):
        """Takes in a new document and returns the a vectorized
        version of it

        inputs
        -------------
        doc : string_type

        returns
        -------------
        tuple (v_id, doc_vector)

        v_id : int_type
                the vector id assigned by the VSMapping, its used as the key
                in the redis db and used to retreive the vector later on

        doc_vector : array_type
                        a vector of the document

        """
        doc_freq_term_matrix = self.count_vect.transform([doc])
        doc_tfidf_matrix = self.tfidf.transform(doc_freq_term_matrix)
        doc_dense = doc_tfidf_matrix.todense()
        doc_vector = doc_dense.tolist()[0]

        # Generate Vector Id and Persist to Redis
        v_id = self._generate_id()
        self.store_val(v_id, pickle.dumps(doc_vector))

        return v_id, doc_vector

    def _generate_id(self):
        """Returns randomly generated id"""
        return utils.generate_id()

    def store_val(self, v_id, v):
        """Writes key, value to redis db"""
        self.r.set(v_id, v)

    def retreive_val(self, v_id):
        """Reads key, value from redis db"""
        return self.r.get(v_id)

    def load_from_mem(self):
        """Loads the count vectorizer, tfidf transformer, and feature names
        from memory

        """
        count_vect = self.retreive_val('count_vect')
        tfidf = self.retreive_val('tfidf')
        feature_names = self.retreive_val('feature_names')
        if not count_vect or not tfidf or not feature_names:
            raise ValueError('Unable to load from Memory.')

        self.count_vect = pickle.loads(count_vect)
        self.tfidf = pickle.loads(tfidf)
        self.feature_names = feature_names


if __name__ == '__main__':
    vsm = VSMapping()
    print vsm._generate_id()
    pass
