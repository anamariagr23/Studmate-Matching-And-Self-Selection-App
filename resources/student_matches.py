from flask import request as flask_request, current_app, jsonify
from flask_restful import Resource
import jwt
from services.compatibility_calculator import CompatibilityCalculator


class StudentMatches(Resource):

    def __init__(self, secret_key):
        self.secret_key = secret_key
        self.compatibility_calculator = CompatibilityCalculator()

    def get(self):
        if "Authorization" in flask_request.headers:
            token = flask_request.headers["Authorization"].split(" ")[0]
            decoded_token = jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])

            student_id=decoded_token['id']

            return {'students': self.compatibility_calculator.get_student_scores(user_id=student_id)}, 200

        else:
            return {'message': 'Access token not found'}, 400

