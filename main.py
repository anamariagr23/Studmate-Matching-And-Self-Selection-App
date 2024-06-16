import os
import ssl
from models.message import Message
import eventlet
from eventlet import wsgi
from flask_socketio import join_room, emit, leave_room
from flask import Flask, jsonify, request
from flask_restful import Api
from flask_cors import CORS
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
from services.encryption_util import encrypt_message
from services.relationships import configure_relationships
from resources.chat import SendMessage, StartConversation, GetConversation, GetConversations
from resources.roomate_request import RoommateRequest, GetUnviewedRequests, MarkRequestsViewed, RoomateCheckRequest

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
api.add_resource(RoommateRequest, '/roommate_requests', '/roommate_requests/<int:request_id>',  '/roommate_requests/target/<int:target_id>')
api.add_resource(GetUnviewedRequests, '/get_unviewed_requests/<int:user_id>')
api.add_resource(MarkRequestsViewed, '/mark_requests_viewed')
api.add_resource(RoomateCheckRequest, '/check_request/<int:requester_id>/<int:target_id>')

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

    # Encrypt the message value
    encrypted_message_value = encrypt_message(message_value)

    # Save the encrypted message to the database
    new_message = Message(conversation_id=room, author_id=author_id, value=encrypted_message_value)
    db.session.add(new_message)
    db.session.commit()

    # Emit the message to all clients in the room with the original message value
    emit('message', {
        'conversation_id': room,
        'author_id': author_id,
        'value': message_value,  # Sending the original message value, not encrypted
        'sent_at': new_message.sent_at.isoformat()
    }, room=room)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        configure_relationships()
    wsgi.server(eventlet.wrap_ssl(eventlet.listen(("127.0.0.1", 5000)),
                                  certfile=app.config['SSL_CERT_PATH'],
                                  keyfile=app.config['SSL_KEY_PATH']), app)

