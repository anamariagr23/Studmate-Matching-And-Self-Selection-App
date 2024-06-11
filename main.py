import os
import ssl
from models.message import Message

import eventlet
from eventlet import wsgi
from flask_socketio import join_room, emit, leave_room

# eventlet.monkey_patch()

context = ssl.SSLContext()
context.load_cert_chain('C:/Users/Anamaria/OneDrive/Desktop/licenta/Certs/cert.pem',
                        'C:/Users/Anamaria/OneDrive/Desktop/licenta/Certs/key.pem')

from flask import Flask, jsonify, request
# from flask_socketio import SocketIO, send, emit
from flask_restful import Api
from flask_cors import CORS
# from auth_middleware import token_required
# from db_app import db
from db_app import create_app, db, socketio
from flask_swagger_ui import get_swaggerui_blueprint
import json

from resources.login import Login
from resources.user import User
from resources.role import Role
from resources.student import Student
from resources.major import Major
from resources.dorm import Dorm
from resources.sex import Sex
from resources.google_login import GoogleLogin
from resources.student_matches import StudentMatches
from resources.student_profile import StudentProfile
from services.relationships import configure_relationships
from resources.chat import SendMessage, StartConversation, GetConversation, GetConversations

# app = Flask(__name__)
# app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:root@localhost/studmate"
# app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
# TO DO figure out how to do this with environment variables later
# app.config["SECRET_KEY"] = "b'7P?DG/tX<siHk"
# socketio = SocketIO(app, cors_allowed_origins="*")

# db.init_app(app)
app = create_app()
api = Api(app)
CORS(app, supports_credentials=True, methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
     allow_headers=["Content-Type", "Authorization"])

api.add_resource(User, '/users')
api.add_resource(Role, '/role')
api.add_resource(Student, '/students')
api.add_resource(Major, '/majors')
api.add_resource(Dorm, '/dorms')
api.add_resource(Sex, '/sexes')
api.add_resource(Login, '/login', resource_class_kwargs={'secret_key': app.config['SECRET_KEY']})
api.add_resource(GoogleLogin, '/google-login', resource_class_kwargs={'secret_key': app.config['SECRET_KEY']})
api.add_resource(StudentProfile, '/student/<int:student_id>',
                 resource_class_kwargs={'secret_key': app.config['SECRET_KEY']})
api.add_resource(StudentMatches, '/student-matches', resource_class_kwargs={'secret_key': app.config['SECRET_KEY']})
api.add_resource(SendMessage, '/send-message')
api.add_resource(StartConversation, '/start-conversation')
api.add_resource(GetConversation, '/get-conversation/<int:user_id>')
api.add_resource(GetConversations, '/get-conversations')

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


# @app.route("/send-message", methods=["POST"])
# def send_message():
#     data = request.json
#     message = data.get("message")
#     username = data.get("username")
#     socketio.emit("receive_message", {"message": message, "username": username})
#     return jsonify({"status": "Message sent"}), 200


@socketio.on("connect")
def handle_connect():
    print("Client connected")

@socketio.on("disconnect")
def handle_disconnect():
    print("Client disconnected")

@socketio.on("join")
def handle_join(data):
    room = data['room']
    join_room(room)
    emit('user_joined', {'room': room}, room=room)

@socketio.on("leave")
def handle_leave(data):
    room = data['room']
    leave_room(room)
    emit('user_left', {'room': room}, room=room)

@socketio.on("message")
def handle_message(data):
    room = data['room']
    message_value = data['message']
    author_id = data['author_id']

    # Save message to the database
    new_message = Message(conversation_id=room, author_id=author_id, value=message_value)
    db.session.add(new_message)
    db.session.commit()

    # Emit the message to all clients in the room
    emit('message', {
        'conversation_id': room,
        'author_id': author_id,
        'value': message_value,
        'sent_at': new_message.sent_at.isoformat()
    }, room=room)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        configure_relationships()
    wsgi.server(eventlet.wrap_ssl(eventlet.listen(("127.0.0.1", 5000)),
                                  certfile='C:/Users/Anamaria/OneDrive/Desktop/licenta/Certs/cert.pem',
                                  keyfile='C:/Users/Anamaria/OneDrive/Desktop/licenta/Certs/key.pem'), app)
    # app.run(debug=True, ssl_context=context)
    # socketio.run(app, host='0.0.0.0', port=5000, debug=True, ssl_context=context)
