from flask import request
from flask_restful import Resource
from db_app import db
from models.student import StudentModel
from models.user import UserModel


class Student(Resource):
    def post(self):
        data = request.get_json()

        new_user = UserModel(email=data['email'], password=data['password'], id_role=3)
        db.session.add(new_user)
        db.session.flush()

        new_student = StudentModel(
            id=new_user.id,
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
