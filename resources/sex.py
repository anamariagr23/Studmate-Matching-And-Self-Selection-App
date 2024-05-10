from flask import request
from flask_restful import Resource
from db_app import db
from models.sex import SexModel


class Sex(Resource):
    def post(self):
        data = request.get_json()

        new_sex = SexModel(name=data['name'])
        db.session.add(new_sex)
        db.session.commit()

        return {'message': 'Sex created successfully'}, 201

    def get(self):
        sexes = SexModel.query.all()
        sex_list = [{'id': sex.id, 'name': sex.name} for sex in sexes]
        return {'sexes': sex_list}
