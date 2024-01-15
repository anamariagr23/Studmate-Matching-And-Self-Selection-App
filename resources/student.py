from flask import request, current_app, jsonify
from flask_restful import Resource
import jwt
from imgurpython import ImgurClient

from auth_middleware import token_required
from db_app import db
from models.student import StudentModel

IMGUR_CLIENT_ID = '3d7b454efa9e6b8'
IMGUR_CLIENT_SECRET = 'c587e08ce1f4b5a0191e20a41875ff4906fa6a50'

client = ImgurClient(IMGUR_CLIENT_ID, IMGUR_CLIENT_SECRET)
class Student(Resource):
    # method_decorators = {'post': [token_required]}

    def post(self):
        data = request.form

        if 'avatar' not in request.files:
            return jsonify({'error': 'No file part'})

        file = request.files['avatar']

        if file.filename == '':
            return jsonify({'error': 'No selected file'})

        uploaded_image = client.upload_from_path(file.filename, config=None, anon=False)

        if "Authorization" in request.headers:
            token = request.headers["Authorization"].split(" ")[1]
            data = jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])
            new_student = StudentModel(
                id=data['user_id'],
                lastname=data['lastname'],
                firstname=data['firstname'],
                id_status=data['id_status'],
                id_major=data['id_major'],
                is_blocked=data['is_blocked'],
                id_sex=data['id_sex'],
                description=data['description'],
                details_completed=data['details_completed'],
                avatar_link=uploaded_image['link']
            )
            db.session.add(new_student)
            db.session.commit()
            return {'message': 'Student created successfully'}, 201
        else:
            return {'message': 'Access token not found'}, 400
