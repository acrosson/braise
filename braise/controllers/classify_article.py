from flask_restful import Resource

class ClassifyArticle(Resource):
    def post(self):
        return {'success': True, 'message': '', 'data': None}
