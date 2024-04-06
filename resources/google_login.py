from models.student import StudentModel
from models.user import UserModel
from models.user_authentication_response import UserAuthenticationResponse
from db_app import db
import jwt
from flask_restful import Resource
from flask import request
import google.oauth2.id_token
import google.auth.transport.requests


class GoogleLogin(Resource):

    def __init__(self, secret_key):
        self.secret_key = secret_key

    def post(self):
        token = request.form.get('credential')
        if not token:
            return {'message': 'No credential token provided'}, 400

        try:
            idinfo = google.oauth2.id_token.verify_oauth2_token(token, google.auth.transport.requests.Request(),
                                                                '676203278903-vpp4otb0bmettevls0eh5trurjshi5u2.apps.googleusercontent.com')

            if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                raise ValueError('Wrong issuer.')

            userid = idinfo['sub']

            auth_response = UserAuthenticationResponse.googleLogin(idinfo['email'])
            # bug that needs to be fixed: user should be able to log in after his user is created
            if auth_response is None:
                new_user = UserModel(email=idinfo['email'], password='',
                                     id_role=3)
                db.session.add(new_user)
                db.session.commit()
                user = UserModel.query.filter_by(email=idinfo['email']).first()
                new_student = StudentModel(
                    id=user.id,
                    lastname=idinfo['family_name'],
                    firstname=idinfo['given_name'],
                    id_status=1,
                    is_blocked=False,
                    details_completed=False,
                    avatar_link=idinfo['picture']
                )
                db.session.add(new_student)
                db.session.commit()
                auth_response = UserAuthenticationResponse.googleLogin(idinfo['email'])

            token = jwt.encode({"id": auth_response.user.id}, self.secret_key, algorithm="HS256")
            auth_response.add_token(token)
            return {"message": "Successfully fetched auth token",
                    "data": auth_response.serialize()
                    }

        except ValueError as e:
            return {'message': str(e)}, 401
