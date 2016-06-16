from models.db import db
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)
from passlib.apps import custom_app_context as pwd_context
from sqlalchemy.exc import IntegrityError
from sqlalchemy import types
from datetime import datetime, timedelta
from enum import Enum
import jwt

class Document(db.Model):

    """Document model

    """

    __tablename__ = 'documents'
    id = db.Column(db.Integer, primary_key=True)
    created_on = db.Column(db.DateTime, server_default=db.func.now())
    updated_on = db.Column(db.DateTime,
                           server_default=db.func.now(),
                           onupdate=db.func.now())
    title = db.Column(db.String(255))
    summary = db.Column(db.String(500))
    url = db.Column(db.String(300))
    raw_filename = db.Column(db.String(100))

    def __init__(self, title, summary, url, raw_filename):
        """Document object Initialization

        inputs
        ------------
        title : string_type
        summary : string_type
        url : string_type
        raw_filename : string_type
                        Filename in S3

        """
        self.title = title
        self.summary = summary
        self.url = url
        self.raw_filename = raw_filename

    def save(self):
        """Saves Document to Database"""
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
            'title': self.title,
            'summary': self.summary,
            'url': self.url,
            'raw_filename': self.raw_filename
        }
