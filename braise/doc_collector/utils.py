"""Utility functions"""

import random
import datetime, time

def generate_id():
    N = 10
    string = 'abcdefghijklmnopqrstuvxyz'
    t = datetime.datetime.now()
    t = int(time.mktime(t.timetuple()))
    filename = ''.join(random.choice(string.lower() + '0123456789') for _ in range(N))
    filename += '-' + str(t)
    return filename
