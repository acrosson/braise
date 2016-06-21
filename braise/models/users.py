from models.db import db
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)
from passlib.apps import custom_app_context as pwd_context
from sqlalchemy.exc import IntegrityError
from sqlalchemy import types
from datetime import datetime, timedelta
from enum import Enum
import jwt

class User(db.Model):

    """User model"""

    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    created_on = db.Column(db.DateTime, server_default=db.func.now())
    updated_on = db.Column(db.DateTime,
                           server_default=db.func.now(),
                           onupdate=db.func.now())
    email = db.Column(db.String(255), index=True, unique=True)
    password_hash = db.Column(db.String(64))
    role = db.Column(types.Enum('user', 'admin'), default='user')
    busy = db.Column(db.Boolean, default=False) 

    def __init__(self, email, password):
        """User object Initialization

        inputs
        ------------
        email : string_type
        password : string_type

        """
        self.email = email
        self.password = self.hash_password(password)

    def save(self):
        """Saves User to Database"""
        try:
            db.session.add(self)
            db.session.commit()
        except IntegrityError as e:
            db.session.rollback()
            raise ValueError('Data invalid. \
                             Cannot create account at this time.')

    def hash_password(self, password):
        """Takes raw password as input as encrypts it and stores it in model"""
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        """Verifies given password matches one stored in model"""
        return pwd_context.verify(password, self.password_hash)

    def generate_auth_token(self, expiration=4320):
        """Generates an authorization token to be stored on client
        expiration time can be set manually, defaults to 3 days (4320 minutes)

        """
        payload = {
            'sub': self.id,
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(minutes=expiration)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
        return token.decode('unicode_escape')
