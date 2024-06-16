from flask import request as flask_request, current_app
from flask_restful import Resource
import jwt

from db_app import db
from models.category import CategoryModel
from models.category_student_self_description import CategoryStudentSelfDescriptionModel
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

            # Fetch the specific student's descriptions
            specific_student_descriptions = CategoryStudentSelfDescriptionModel.query.filter_by(student_id=student_id).all()

            # Fetch all categories to map id to title
            categories = {category.id: category.title for category in CategoryModel.query.all()}

            response_data = {
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
                'categories': [
                    {
                        'category': categories[desc.category_id],
                        'answer': desc.answer,
                        'importance': desc.importance_score
                    } for desc in specific_student_descriptions
                ]
            }

            if logged_in_student_id != student_id:
                # Calculate compatibility score between the logged-in user and the profile being viewed
                compatibility_score = self.compatibility_calculator.get_student_score_with_specific_student(
                    user_id=logged_in_student_id,
                    specific_student_id=student_id
                )

                if not compatibility_score:
                    return {'message': 'No compatibility score found for the selected student'}, 404

                response_data['compatibility_score'] = compatibility_score['total_score']
                response_data['categories'] = compatibility_score['categories']  # Override categories with detailed scores

            return response_data, 200

        else:
            return {'message': 'Access token not found'}, 400
