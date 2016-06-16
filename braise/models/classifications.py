from models.db import db
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)
from passlib.apps import custom_app_context as pwd_context
from sqlalchemy.exc import IntegrityError
from sqlalchemy import types
from datetime import datetime, timedelta
from enum import Enum
import jwt

class Classification(db.Model):

    """Classification model

    Stores all items that were classified by User or by other entity

    """

    __tablename__ = 'classifications'
    id = db.Column(db.Integer, primary_key=True)
    created_on = db.Column(db.DateTime, server_default=db.func.now())
    updated_on = db.Column(db.DateTime,
                           server_default=db.func.now(),
                           onupdate=db.func.now())
    document_id = db.Column(db.Integer, db.ForeignKey('documents.id'))
    prediction_id = db.Column(db.Integer, db.ForeignKey('predictions.id'))
    prediction_type = db.Column(types.Enum('document'), default='document')
    class_label = db.Column(db.Integer)

    def __init__(self, document_id, prediction_id, class_label):
        """Prediction object Initialization

        inputs
        ------------
        document_id : int_type
                        ForeignKey to document.id
        prediction_id : int_type
                        ForeignKey to predictions.id
        class_label : int_type
                      Class label

        """
        self.document_id = document_id
        self.prediction_id = prediction_id
        self.class_label = class_label

    def save(self):
        """Saves Classifcation to Database"""
        try:
            db.session.add(self)
            db.session.commit()
        except IntegrityError as e:
            db.session.rollback()
            raise ValueError('Data invalid. \
                             Cannot create document at this time.')

    def to_dict(self):
        return {
            'id': self.id,
            'created_on': str(self.created_on),
            'document_id': self.prediction_id,
            'prediction_id': self.prediction_id,
            'prediction_type': self.prediction_type,
            'class_label': self.class_label,
        }
