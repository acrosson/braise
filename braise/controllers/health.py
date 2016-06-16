from flask_restful import Resource

class Health(Resource):
    def get(self):
        return {'success': True, 'message': '', 'data': None}
    def post(self):
        pass
