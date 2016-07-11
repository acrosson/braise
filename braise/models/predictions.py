from models.db import db
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)
from passlib.apps import custom_app_context as pwd_context
from sqlalchemy.exc import IntegrityError
from sqlalchemy import types
from datetime import datetime, timedelta
from enum import Enum
import jwt

class Prediction(db.Model):

    """Prediction model

    Used to store document predictions for users

    """

    __tablename__ = 'predictions'
    id = db.Column(db.Integer, primary_key=True)
    created_on = db.Column(db.DateTime, server_default=db.func.now())
    updated_on = db.Column(db.DateTime,
                           server_default=db.func.now(),
                           onupdate=db.func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    document_id = db.Column(db.Integer, db.ForeignKey('documents.id'))
    onboard = db.Column(db.Boolean, default=False)
    viewed_on = db.Column(db.DateTime)
    random_pred = db.Column(db.Boolean, default=False)

    def __init__(self, user_id, document_id, onboard=False, random_pred=False):
        """Prediction object Initialization

        inputs
        ------------
        user_id : int_type
                    ForeignKey to user.id
        document_id : int_type
                        ForeignKey to document.id
        onboard : Boolean (optional)

        """
        self.user_id = user_id
        self.document_id = document_id
        self.onboard = onboard
        self.random_pred = random_pred

    def save(self):
        """Saves Predictions to Database"""
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
            'user_id': self.user_id,
            'document_id': self.document_id,
            'onboard': self.onboard,
            'viewed_on': str(self.viewed_on),
            'random_pred': int(self.random_pred)
        }
