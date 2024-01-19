import os

from flask import Flask, jsonify
from flask_restful import Api
from flask_cors import CORS
from auth_middleware import token_required
from db_app import db
from flask_swagger_ui import get_swaggerui_blueprint
import json


from resources.login import Login
from resources.user import User
from resources.role import Role
from resources.student import Student
from resources.major import Major

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@localhost/studmate'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# TO DO figure out how to do this with environment variables later
app.config['SECRET_KEY'] = "b'7P?DG/tX<siHk"

db.init_app(app)
api = Api(app)
CORS(app, supports_credentials=True, methods=["GET", "POST", "PUT", "DELETE"], allow_headers=["Content-Type", "Authorization"])

api.add_resource(User, '/users')
api.add_resource(Role, '/role')
api.add_resource(Student, '/students')
api.add_resource(Major, '/majors')
api.add_resource(Login, '/login', resource_class_kwargs={'secret_key': app.config['SECRET_KEY']})

SWAGGER_URL = '/swagger'
API_URL = '/swagger.json'
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Sample API"
    }
)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)


@app.route('/swagger.json')
def swagger():
    with open('swagger.json', 'r') as f:
        return jsonify(json.load(f))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
