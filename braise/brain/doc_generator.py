import cPickle as pickle
from scipy import spatial
from sklearn.cluster import MiniBatchKMeans
from doc_collector.vsmapping import VSMapping

class DocGenerator(object):

    """DocGenerator

    The DocGenerator used to predict new documents for users based on
    similarity score of previous choices by user.

    Attributes
    ---------------
    users : dict_type
            stores a dictionary of user ids with a KMeans Classifier as the value

    vsm : VSMapping
            Used to load vectors from memory

    """

    def __init__(self, n_clusters=8):
        self.users = {}
        self.vsm = VSMapping()
        self.vsm.load_from_mem()
        self.n_clusters = n_clusters

    def _compute_cosine(self, a, b):
        """Return the cosine similarity of two vectors"""
        return 1 - spatial.distance.cosine(a, b)

    def fit(self, user_id, v_ids):
        """Initial fit for user with vectors. If length of vectors is less
        than cluster size, raise exception

        """
        if len(v_ids) < self.n_clusters:
            raise ValueError('Number of vectors must be greater than or equal\
                             to the n_clusters')

        # Load or Initialize the model
        model = MiniBatchKMeans(n_clusters=8)

        # Fit the model with new data
        vectors = [self.vsm.retreive_val(v_id) for v_id in v_ids]
        model.fit(vectors)
        self.users[user_id] = model

    def batch_fit(self, data):
        """Batch fits all user data and vectors into unique classifiers

        inputs
        -----------
        data : list_type
                A list of dictionaries with {user_id, vectors} pairs

        """
        for d in data:
            self.fit(d[0], d[1])

    def partial_fit(self, user_id, v_id):
        """Partial fits user model"""
        if user_id in self.users:
            self.users[user_id].partial_fit(self.vsm.retreive_val(v_id))
        else:
            raise ValueError('User not in model')

    def predict(self, user_id, v_ids, rand_v_ids):
        """Returns predicted vector ids for top 5 predictions. Otherwise
        returns random

        """
        if user_id not in self.users:
            raise ValueError('User not in model')

        # Load vectors and make predictions
        vectors = [self.vsm.retreive_val(v_id) for v_id in v_ids]
        preds = self.users[user_id].predict(vectors)

        # Score each prediction by measuring the cosine distance
        # between the cluster centroid and the given vector
        # Only those who's similarity is greater than 0.20 are used
        scores = [(self._compute_cosine(self.users[user_id].cluster_centers_[c],
                                       vectors[i]), i) for i, c in enumerate(preds)]
        scores = sorted(scores, reverse=True, key=get_key)
        top_v_ids = [v_ids[i] for s, i in scores if s >= 0.20]

        # If the predicted vectors is less than five, choose randomly for the
        # the remaining
        if len(top_v_ids) < 5:
            top_v_ids += rand_v_ids[:5-len(top_v_ids)]

        print top_v_ids

    def load_from_disk(self):
        pass

    def persist_to_disk(self):
        pass
