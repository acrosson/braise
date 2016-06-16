import requests, json
from flask import jsonify, g
from flask_restful import fields, marshal_with, reqparse, request, Resource
from models.predictions import Prediction
from utils.auth import login_required

post_parser = reqparse.RequestParser()
post_parser.add_argument(
    'user_id',
    dest='user_id', location='form',
    required=True, help='The user_id is invalid',
)
post_parser.add_argument(
    'document_id', type=int,
    dest='document_id', location='form',
    required=True, help='The document_id is invalid',
)

def parseint(string):
    return int(string) if str(string).isdigit() else 0

class PredictionController(Resource):

    """A handler for all /predictions api requests

    methods
    ---------------
    get : returns a list of all predictions

    post : creates a prediction, or returns false if something goes wrong

    """

    # @login_required('admin')
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('p')
        parser.add_argument('min_id')
        args = parser.parse_args()
        page_size = 10
        page = parseint(args.p)
        min_id = parseint(args.min_id)
        predictions = Prediction.query\
                        .filter(Prediction.id > min_id)\
                        .order_by('id desc')\
                        .limit(10).offset(page*page_size)

        return {'success': True, 'message': '',
                'data': [p.to_dict() for p in predictions]}

    # @login_required('admin')
    def post(self):
        args = post_parser.parse_args()
        prediction = Prediction(args.user_id,
                                args.document_id)

        # Save to db
        try:
            prediction.save()
            data = {'prediction_id': prediction.id}
            return {'success': True, 'message':
                    'Prediction successfully submitted', 'data': data}
        except ValueError as e:
            return {'success': False, 'message': str(e), 'data': None}
