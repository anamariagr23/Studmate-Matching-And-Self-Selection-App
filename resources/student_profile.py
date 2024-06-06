from flask import request as flask_request, current_app
from flask_restful import Resource
import jwt
from services.compatibility_calculator import CompatibilityCalculator
from models.student import StudentModel


class StudentProfile(Resource):

    def __init__(self, secret_key):
        self.secret_key = secret_key
        self.compatibility_calculator = CompatibilityCalculator()

    def get(self, student_id):
        if "Authorization" in flask_request.headers:
            token = flask_request.headers["Authorization"].split(" ")[1]
            decoded_token = jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])

            logged_in_student_id = decoded_token['id']

            # Fetch the profile of the student with the given student_id
            student = StudentModel.query.filter_by(id=student_id).first()
            if not student:
                return {'message': 'Student not found'}, 404

            # Calculate compatibility score between the logged-in user and the profile being viewed
            compatibility_score = self.compatibility_calculator.get_student_score_with_specific_student(
                user_id=logged_in_student_id,
                specific_student_id=student_id
            )

            if not compatibility_score:
                return {'message': 'No compatibility score found for the selected student'}, 404

            return {
                       'student': {
                           'id': student.id,
                           'firstname': student.firstname,
                           'lastname': student.lastname,
                           'status': student.status.name if student.status else None,
                           'major': student.major.name if student.major else None,
                           'year_of_study': student.year_of_study,
                           'description': student.description,
                           'avatar_link': student.avatar_link,
                       },
                       'compatibility_score': compatibility_score['total_score'],
                       'categories': compatibility_score['categories']
                   }, 200

        else:
            return {'message': 'Access token not found'}, 400
