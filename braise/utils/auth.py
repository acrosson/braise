import jwt
import config
from functools import wraps
from jwt import DecodeError, ExpiredSignature
from datetime import datetime, timedelta
from flask import Flask, abort, request, jsonify, g, url_for
from models.users import User

def create_token(user):
    """Creates a user token storing user_id and exp time"""
    payload = {
        'sub': user.id,
        'iat': datetime.utcnow(),
        'exp': datetime.utcnow() + timedelta(days=1)
    }
    token = jwt.encode(payload, config.SECRET_KEY, algorithm='HS256')
    return token.decode('unicode_escape')


def parse_token(req):
    """Confirms that a token is valid"""
    auth_string_list = req.headers.get('Authorization').split()
    # Check in correct format i.e. Bearer: 39xds03lda0...
    if len(auth_string_list) == 1:
        raise ValueError('Authorization has invalid format')
    else:
        token = auth_string_list[1]
        data = jwt.decode(token, config.SECRET_KEY, algorithms='HS256')
        return data

# Login decorator function
def login_required(role):
    """Login decorator function. Used to wrap API methods than need to be
    restricted to certain user role types (ie admin).

    """
    def real_decorator(f):
        def decorated_function(*args, **kwargs):
            if not request.headers.get('Authorization'):
                response = jsonify(message='Missing authorization header')
                response.status_code = 401
                return response

            try:
                payload = parse_token(request)
            except DecodeError:
                response = jsonify(message='Token is invalid')
                response.status_code = 401
                return response
            except ExpiredSignature:
                response = jsonify(message='Token has expired')
                response.status_code = 401
                return response
            except ValueError as error:
                response = jsonify(message=str(error))
                response.status_code = 401
                return response

            # pass user id to flask request global
            g.user_id = payload['sub']

            # Check for admin roles
            if role == 'admin':
                # find User
                user = User.query.filter(User.id == g.user_id).first()
                if not user or user.role != 'admin':
                    response = jsonify(message='You are not authorized')
                    response.status_code = 401
                    return response

            # user = User
            return f(*args, **kwargs)

        return decorated_function
    return real_decorator
