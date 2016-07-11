import requests, json
from flask import jsonify, g
from flask_restful import fields, marshal_with, reqparse, request, Resource
from models.documents import Document
from models.classifications import Classification
from utils.auth import login_required

document_parser = reqparse.RequestParser()
document_parser.add_argument(
    'title',
    dest='title', location='form',
    required=True, help='The title is invalid',
)
document_parser.add_argument(
    'summary',
    dest='summary', location='form',
    required=True, help='The summary is invalid',
)
document_parser.add_argument(
    'url',
    dest='url', location='form',
    required=True, help='The url is invalid',
)
document_parser.add_argument(
    'raw_filename',
    dest='raw_filename', location='form',
    required=True, help='The raw filename is invalid',
)

classify_parser = reqparse.RequestParser()
classify_parser.add_argument(
    'prediction_id', type=int,
    dest='prediction_id', location='form',
    required=True, help='The prediction_id is invalid',
)
classify_parser.add_argument(
    'class_label', type=int,
    dest='class_label', location='form',
    required=True, help='The class_label is invalid',
)


def parseint(string):
    return int(string) if str(string).isdigit() else 0

def abort_if_doc_doesnt_exist(document_id):
    return
    # if document not in TODOS:
        # abort(404, message="Document {} doesn't exist".format(todo_id))

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
        args = document_parser.parse_args()
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

class DocumentClassifyController(Resource):

    """A handler for all /documents/<document_id>/classify api requests

    methods
    ---------------
    post : classified a document

    """

    def post(self, document_id):
        args = classify_parser.parse_args()
        classification = Classification(document_id,
                                        args.prediction_id,
                                        args.class_label)

        # Save to db
        try:
            classification.save()
            data = {'classification_id': classification.id}
            return {'success': True, 'message':
                    'Classification successfully submitted', 'data': data}
        except ValueError as e:
            return {'success': False, 'message': str(e), 'data': None}
