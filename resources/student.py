from flask import request, current_app
from flask_restful import Resource
import jwt

from auth_middleware import token_required
from db_app import db
from models.student import StudentModel


class Student(Resource):
    method_decorators = {'post': [token_required]}

    def post(self):
        data = request.get_json()

        # new_user = UserModel(email=data['email'], password=data['password'], id_role=3)
        # db.session.add(new_user)
        # db.session.flush()
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
                details_completed=data['details_completed']
            )
            db.session.add(new_student)
            db.session.commit()
            return {'message': 'Student created successfully'}, 201
        else:
            return {'message': 'Access token not found'}, 400
