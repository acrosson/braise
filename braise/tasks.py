#!/usr/bin/env python

"""Celery Queue Tasks

INSTRUCTIONS TO RUN
--------------------
celery -A tasks worker --loglevel=info

"""

from brain import predictions
from celery import Celery

app = Celery('tasks', broker='redis://localhost:6379/2')

@app.task
def generate_pred(user_id):
    """Genereates predictions for user"""
    predictions.generate_pred(user_id)

@app.task
def set_preds_as_viewed(preds):
    """Sets current predictions as viewed = True"""
    predictions.set_preds_as_viewed(preds)
