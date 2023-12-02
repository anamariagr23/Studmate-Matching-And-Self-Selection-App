from flask import request
from flask_restful import Resource
from db_app import db
from models.major import MajorModel


class Major(Resource):
    def post(self):
        data = request.get_json()

        new_major = MajorModel(name=data['name'])
        db.session.add(new_major)
        db.session.commit()

        return {'message': 'Major created successfully'}, 201

    def get(self):
        majors = MajorModel.query.all()
        major_list = [{'id': major.id, 'name': major.name} for major in majors]
        return {'majors': major_list}
