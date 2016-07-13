#!/usr/bin/env python

"""Celery Queue Tasks

INSTRUCTIONS TO RUN
--------------------
celery -A tasks worker --loglevel=info

"""

from brain import predictions
from celery import Celery

r = 'redis://:br41s3db93lxpa@braise.tech:6379/0'
app = Celery('tasks', broker=r)

@app.task
def generate_pred(user_id):
    """Genereates predictions for user"""
    predictions.generate_pred(user_id)

@app.task
def set_preds_as_viewed(preds):
    """Sets current predictions as viewed = True"""
    predictions.set_preds_as_viewed(preds)
