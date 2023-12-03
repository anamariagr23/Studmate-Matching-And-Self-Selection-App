from flask import jsonify
from flask_restful import Resource, reqparse
from models.user import UserModel
from db_app import db
from werkzeug.security import generate_password_hash, check_password_hash


class User(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('email', type=str, help='Email of the user', required=True)
        self.parser.add_argument('password', type=str, help='Password of the user', required=True)
        self.parser.add_argument('id_role', type=int, help='ID of the role', required=True)

    def get(self):
        users = UserModel.query.all()
        user_list = [{'id': user.id, 'email': user.email, 'id_role': user.id_role} for user in users]
        return jsonify(user_list)

    def post(self):
        args = self.parser.parse_args()
        new_user = UserModel(email=args['email'], password=generate_password_hash(args['password']),
                             id_role=args['id_role'])
        db.session.add(new_user)
        db.session.commit()
        return {'message': 'User created successfully'}, 201
