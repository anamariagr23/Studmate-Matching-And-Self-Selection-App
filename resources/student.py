from flask import request as flask_request, current_app, jsonify
from flask_restful import Resource
import jwt
from auth_middleware import token_required
from db_app import db
from models.category import CategoryModel
from models.student import StudentModel
from models.category_student_self_description import CategoryStudentSelfDescriptionModel
import requests

IMGUR_CLIENT_ID = '3d7b454efa9e6b8'
IMGUR_CLIENT_SECRET = 'c587e08ce1f4b5a0191e20a41875ff4906fa6a50'


# imgur_client = Imgur({"client_id": IMGUR_CLIENT_ID,
#                       "client_secret": IMGUR_CLIENT_SECRET})


class Student(Resource):
    # method_decorators = {'post': [token_required]}

    def patch(self):
        data = flask_request.form

        # if 'file' not in flask_request.files:
        #     return jsonify({'error': 'No file part'})
        #
        # file = flask_request.files['file']
        #
        # if file.filename == '':
        #     return jsonify({'error': 'No selected file'})

        # url = "https://api.imgur.com/3/image"
        # payload = {'image': flask_request.files['file'].read()}
        # files = []
        # headers = {
        #     'Authorization': 'Client-ID e4375b375a003c4'
        # }
        # response = requests.request("POST", url, headers=headers, data=payload, files=files)

        if "Authorization" in flask_request.headers:
            token = flask_request.headers["Authorization"].split(" ")[1]
            decoded_token = jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])

            updated_student = StudentModel.query.filter_by(id=decoded_token['id']).one()

            # updated_student.firstname = data['firstname']
            # updated_student.lastname = data['lastname']
            updated_student.id_status = 1
            updated_student.id_major = data['major']
            updated_student.is_blocked = False
            updated_student.id_sex = data['sex']
            updated_student.description = data['description']
            updated_student.details_completed = True
            updated_student.dorm_id = data['dorm']
            updated_student.year_of_study = data['year_of_study']

            categories = [
                ('cleanlinessHabits', 'cleanlinessHabitsImportance', 1),
                ('sleepingPatterns', 'sleepingPatternsImportance', 2),
                ('noiseTolerance', 'noiseToleranceImportance', 3),
                ('belongingsSharing', 'belongingsSharingImportance', 4),
                ('guestPolicy', 'guestPolicyImportance', 5),
                ('sharingResponsibilities', 'sharingResponsibilitiesImportance', 6),
                ('itemsSharing', 'itemsSharingImportance', 7),
                ('temperaturePreferences', 'temperaturePreferencesImportance', 8),
                ('hobbies', 'hobbiesImportance', 9),
                ('personalValues', 'personalValuesImportance', 10)
            ]

            for answer_field, importance_field, category_id in categories:
                answer = data.get(answer_field)
                importance_score = data.get(importance_field)

                if answer and importance_score:
                    description_entry = CategoryStudentSelfDescriptionModel.query.filter_by(
                        student_id=updated_student.id, category_id=category_id).first()
                    if description_entry:
                        description_entry.answer = answer
                        description_entry.importance_score = importance_score
                    else:
                        new_description = CategoryStudentSelfDescriptionModel(
                            student_id=updated_student.id,
                            category_id=category_id,
                            answer=answer,
                            importance_score=importance_score
                        )
                        db.session.add(new_description)

            # updated_student = StudentModel(
            #     id=decoded_token['id'],
            #     lastname=data['lastname'],
            #     firstname=data['firstname'],
            #     id_status=1,
            #     id_major=data['major'],
            #     is_blocked=False,
            #     id_sex=data['sex'],
            #     description=data['description'],
            #     details_completed=True,
            #     avatar_link=None
            # )
            # db.session.update(updated_student)
            db.session.commit()
            return {'message': 'Student created successfully'}, 201
        else:
            return {'message': 'Access token not found'}, 400

    def get(self):
        try:
            students = StudentModel.query.all()
            students_data = [{
                'id': student.id,
                'lastname': student.lastname,
                'firstname': student.firstname,
                'id_status': student.id_status,
                'id_major': student.id_major,
                'is_blocked': student.is_blocked,
                'id_sex': student.id_sex,
                'description': student.description,
                'details_completed': student.details_completed,
                'dorm_id': student.dorm_id,
                'avatar_link': student.avatar_link,
                'year_of_study': student.year_of_study
            } for student in students]

            return {'students': students_data}, 200
        except Exception as e:
            # It's a good practice to log the actual error for debugging
            current_app.logger.error(f"Error fetching students: {e}")
            return {'error': 'Error fetching students'}, 500



class StudentCategories(Resource):
    # def get(self):
    #     if "Authorization" in flask_request.headers:
    #         token = flask_request.headers["Authorization"].split(" ")[1]
    #         decoded_token = jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])
    #
    #         student = StudentModel.query.filter_by(id=decoded_token['id']).one_or_none()
    #
    #         if student:
    #             student_data = {
    #                 'id': student.id,
    #                 'lastname': student.lastname,
    #                 'firstname': student.firstname,
    #                 'id_status': student.id_status,
    #                 'id_major': student.id_major,
    #                 'is_blocked': student.is_blocked,
    #                 'id_sex': student.id_sex,
    #                 'description': student.description,
    #                 'details_completed': student.details_completed,
    #                 'dorm_id': student.dorm_id,
    #                 'avatar_link': student.avatar_link,
    #                 'year_of_study': student.year_of_study,
    #                 'categories': [{
    #                     'category_id': category.category_id,
    #                     'answer': category.answer,
    #                     'importance_score': category.importance_score
    #                 } for category in student.self_descriptions]  # Use the correct relationship
    #             }
    #             return {'student': student_data}, 200
    #         else:
    #             return {'message': 'Student not found'}, 404
    #     else:
    #         return {'message': 'Access token not found'}, 400

    def get(self):
        if "Authorization" in flask_request.headers:
            token = flask_request.headers["Authorization"].split(" ")[1]
            decoded_token = jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])

            student = StudentModel.query.filter_by(id=decoded_token['id']).one_or_none()

            if student:
                categories = db.session.query(
                    CategoryStudentSelfDescriptionModel,
                    CategoryModel.title
                ).join(CategoryModel, CategoryStudentSelfDescriptionModel.category_id == CategoryModel.id).filter(
                    CategoryStudentSelfDescriptionModel.student_id == student.id
                ).all()

                categories_data = [{
                    'category_id': category.CategoryStudentSelfDescriptionModel.category_id,
                    'answer': category.CategoryStudentSelfDescriptionModel.answer,
                    'importance_score': category.CategoryStudentSelfDescriptionModel.importance_score,
                    'category': category.title
                } for category in categories]

                student_data = {
                    'id': student.id,
                    'lastname': student.lastname,
                    'firstname': student.firstname,
                    'id_status': student.id_status,
                    'id_major': student.id_major,
                    'is_blocked': student.is_blocked,
                    'id_sex': student.id_sex,
                    'description': student.description,
                    'details_completed': student.details_completed,
                    'dorm_id': student.dorm_id,
                    'avatar_link': student.avatar_link,
                    'year_of_study': student.year_of_study,
                    'categories': categories_data
                }
                return {'student': student_data}, 200
            else:
                return {'message': 'Student not found'}, 404
        else:
            return {'message': 'Access token not found'}, 400

