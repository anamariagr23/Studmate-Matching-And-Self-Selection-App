from flask import jsonify
from flask_restful import Resource, reqparse
from models.role import RoleModel
from db_app import db

class Role(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('name', type=str, help='Name of the rol', required=True)

    def post(self):
        args = self.parser.parse_args()
        new_role = RoleModel(name=args['name'])
        db.session.add(new_role)
        db.session.commit()
        return {'message': 'Role created successfully'}, 201