#!/usr/bin/env python
import os
from flask import Flask, abort, request, jsonify, g, url_for
from flask_restful import Api
from flask.ext.cors import CORS
from models.db import db
from controllers.health import Health
import config

##
## Initialization
##
app = Flask(__name__)
app.config['SECRET_KEY'] = config.SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = config.DB_URI
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
api = Api(app)
cors = CORS(app, resources={r"/*": {"origins": "*"}})

##
## Extensions
##
db.init_app(app)

##
## API Routing
##
api.add_resource(Health, '/health')

##
## Run App
##
if __name__ == '__main__':
    if not os.path.exists('db.sqlite'):
        with app.app_context():
            print 'creating db'
            db.create_all()
    app.run(debug=True, threaded=True)
