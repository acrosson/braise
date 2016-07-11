"""Utility functions"""

import random
import datetime, time
from nltk.corpus import stopwords
stop = stopwords.words('english')

def generate_id():
    N = 10
    string = 'abcdefghijklmnopqrstuvxyz'
    t = datetime.datetime.now()
    t = int(time.mktime(t.timetuple()))
    filename = ''.join(random.choice(string.lower() + '0123456789') for _ in range(N))
    filename += '-' + str(t)
    return filename

def remove_stop_words(document):
    """Returns document without stop words"""
    document = ' '.join([i for i in document.split() if i not in stop])
    return document
