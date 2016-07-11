import requests, json
from flask import jsonify, g
from flask_restful import fields, marshal_with, reqparse, request, Resource
from models.predictions import Prediction
from models.documents import Document
from models.users import User
from utils.auth import login_required
from tasks import generate_pred, set_preds_as_viewed

def parseint(string):
    return int(string) if str(string).isdigit() else 0

class NewsController(Resource):

    """A handler for all /new  api requests

    methods
    ---------------
    get : returns a list of all predictions
            if no new predictions, add Prediction Generator request to queue

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
                        .filter(Prediction.viewed_on == None)\
                        .order_by('id desc')\
                        .limit(10).offset(page*page_size)

        # If there are no predictions, generated some queue queue
        if not predictions.first():
            user = User.query.filter(User.id == 1).first()
            if user:
                if user.busy == False:
                    # Set user busy to True to prevent duplicate preds
                    #user.busy = True
                    try:
                        #user.save()

                        # Add GeneratePrediction queue
                        generate_pred.delay(1)
                    except ValueError as e:
                        print e
                return {'success': False, 'message': 'Generating news ...',
                        'data': {'generating': True}}

        # Set predictions to viewed
        set_preds_as_viewed.delay([p.to_dict() for p in predictions])

        doc_ids = [p.to_dict()['document_id'] for p in predictions]

        preds = [p.to_dict() for p in predictions]

        docs = [d.to_dict() for d in Document.query.filter(Document.id.in_(doc_ids))]
        for i, d in enumerate(docs):
            d['random_pred'] = preds[i]['random_pred']

        for i, doc in enumerate(docs):
            docs[i]['prediction_id'] = preds[i]['id']

        return {'success': True, 'message': '',
                'data': docs}

