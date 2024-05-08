from flask import request as flask_request, current_app, jsonify
from flask_restful import Resource
import jwt
from auth_middleware import token_required
from db_app import db
from models.student import StudentModel
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

            updated_student.firstname = data['firstname']
            updated_student.lastname = data['lastname']
            updated_student.id_status = 1
            updated_student.id_major = data['major']
            updated_student.is_blocked = False
            updated_student.id_sex = data['sex']
            updated_student.description = data['description']
            updated_student.details_completed = True

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
                'avatar_link': student.avatar_link
            } for student in students]

            return {'students': students_data}, 200
        except Exception as e:
            # It's a good practice to log the actual error for debugging
            current_app.logger.error(f"Error fetching students: {e}")
            return {'error': 'Error fetching students'}, 500
