from flask import jsonify, g
from flask_restful import fields, marshal_with, reqparse, request, Resource
from models.users import User
from validate_email import validate_email
from utils.auth import login_required
from sqlalchemy.exc import IntegrityError
from datetime import datetime

def email(email_str):
    """Return email_str if valid, raise an exception in other case."""
    if validate_email(email_str):
        return email_str
    else:
        raise ValueError('{} is not a valid email'.format(email_str))

def password(password_str):
    """Checks if password length is greater than 4, else raises error"""
    if len(password_str) > 4:
        return password_str
    else:
        raise ValueError('Invalid password')

post_parser = reqparse.RequestParser()
post_parser.add_argument(
    'email', dest='email',
    type=email, location='form',
    required=True, help='The user\'s email is invalid',
)
post_parser.add_argument(
    'password', dest='password',
    type=password, location='form',
    required=True, help='The user\'s password is invalid',
)

user_fields = {
    'email': fields.String,
    'password': fields.String,
}

class UserController(Resource):

    """A handler for all /user api requests

    methods
    ---------------
    post : creates user, or returns false if user already exists

    """

    def post(self):
        """Checks if user already exists, otherwise creates a new User in db"""
        args = post_parser.parse_args()
        user = User(args.email, args.password)

        # Check if already registered
        user_already_exists = User.query.filter(User.email == args.email).first()
        if user_already_exists:
            return {'success': False, 'message': 'That user already exists', 'data': None}

        # Try saving the user to db
        try:
            user.save()
            return {'success': True, 'message': 'User successfully added', 'data': None}
        except ValueError as e:
            return {'success': False, 'message': str(e), 'data': None}

class UserAuthController(Resource):

    """UserAuthController is used to authorize a users credentials

    methods
    --------------
    post : validates a auth token is valid

    """

    def post(self):
        """Validates user by checking email and password"""
        args = post_parser.parse_args()
        user = User.query.filter(User.email == args.email).first()
        if user and user.verify_password(args.password):
            auth_token = user.generate_auth_token()
            return {'success': True, 'message': 'Auth token successfully authorized', 'data': {'auth_token': auth_token} }
        else:
            return {'success': False, 'message': 'Invalid credentials.', 'data': None}
