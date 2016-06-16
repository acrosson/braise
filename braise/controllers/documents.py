import requests, json
from flask import jsonify, g
from flask_restful import fields, marshal_with, reqparse, request, Resource
from models.documents import Document
from utils.auth import login_required

post_parser = reqparse.RequestParser()
post_parser.add_argument(
    'title',
    dest='title', location='form',
    required=True, help='The title is invalid',
)
post_parser.add_argument(
    'summary',
    dest='summary', location='form',
    required=True, help='The summary is invalid',
)
post_parser.add_argument(
    'url',
    dest='url', location='form',
    required=True, help='The url is invalid',
)
post_parser.add_argument(
    'raw_filename',
    dest='raw_filename', location='form',
    required=True, help='The raw filename is invalid',
)

def parseint(string):
    return int(string) if str(string).isdigit() else 0

class DocumentController(Resource):

    """A handler for all /documents api requests

    methods
    ---------------
    get : return list of documents paged with page number and min_id
            p : page number
            min_id : the minimum document number

    post : creates document, or returns false if doc already exists

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
        documents = Document.query\
                    .filter(Document.id > min_id)\
                    .order_by('id desc')\
                    .limit(10).offset(page*page_size)

        return {'success': True, 'message': '',
                'data': [d.to_dict() for d in documents]}

    # @login_required('admin')
    def post(self):
        args = post_parser.parse_args()
        document = Document(args.title,
                            args.summary,
                            args.url,
                            args.raw_filename)

        # Save to db
        try:
            document.save()
            data = {'document_id': document.id}
            return {'success': True, 'message':
                    'Message successfully submitted', 'data': data}
        except ValueError as e:
            return {'success': False, 'message': str(e), 'data': None}
