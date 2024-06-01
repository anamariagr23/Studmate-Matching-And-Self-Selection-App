from flask import request
import jwt
import re
from flask_restful import Resource

from models.user import UserModel
# import jsonpickle
from flask import jsonify

from models.user_authentication_response import UserAuthenticationResponse


class Login(Resource):
    def __init__(self, secret_key):
        self.secret_key = secret_key

    def post(self):
        try:
            data = request.json
            if not data:
                return {
                           "message": "Please provide user details",
                           "data": None,
                           "error": "Bad request"
                       }, 400
            # validate input
            # is_validated = validate_email_and_password(data.get('email'), data.get('password'))
            is_validated = True
            if is_validated is not True:
                return dict(message='Invalid data', data=None, error=is_validated), 400
            auth_response = UserAuthenticationResponse.login(data['email'], data['password'])
            if auth_response:
                try:
                    # token should expire after 24 hrs
                    token = jwt.encode({"id": auth_response.user.id}, self.secret_key, algorithm="HS256")
                    auth_response.add_token(token)

                    return {
                        "message": "Successfully fetched auth token",
                        "data": auth_response.serialize()
                    }
                except Exception as e:
                    return {
                               "error": "Something went wrong",
                               "message": str(e)
                           }, 500
            return {
                       "message": "Error fetching auth token!, invalid email or password",
                       "data": None,
                       "error": "Unauthorized"
                   }, 404
        except Exception as e:
            return {
                       "message": "Something went wrong!",
                       "error": str(e),
                       "data": None
                   }, 500


def validate_email_and_password(email, password):
    """Email and Password Validator"""
    if not (email and password):
        return {
            'email': 'Email is required',
            'password': 'Password is required'
        }
    if not validate_email(email):
        return {
            'email': 'Email is invalid'
        }
    if not validate_password(password):
        return {
            'password': 'Password is invalid, Should be atleast 8 characters with \
                upper and lower case letters, numbers and special characters'
        }
    return True


def validate(data, regex):
    """Custom Validator"""
    return True if re.match(regex, data) else False


def validate_password(password: str):
    """Password Validator"""
    reg = r"\b^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{8,20}$\b"
    return validate(password, reg)


def validate_email(email: str):
    """Email Validator"""
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    return validate(email, regex)
