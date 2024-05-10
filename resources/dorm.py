from flask import request
from flask_restful import Resource
from db_app import db
from models.dorm import DormModel


class Dorm(Resource):
    def post(self):
        data = request.get_json()

        new_dorm = DormModel(name=data['name'])
        db.session.add(new_dorm)
        db.session.commit()

        return {'message': 'Dorm created successfully'}, 201

    def get(self):
        dorms = DormModel.query.all()
        dorm_list = [{'id': dorm.id, 'name': dorm.name} for dorm in dorms]
        return {'dorms': dorm_list}
