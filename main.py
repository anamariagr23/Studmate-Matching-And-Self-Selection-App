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
from resources.student import Student, StudentCategories
from resources.major import Major
from resources.dorm import Dorm
from resources.sex import Sex
from resources.google_login import GoogleLogin
from resources.student_matches import StudentMatches
from resources.student_profile import StudentProfile
from services.encryption_util import encrypt_message
from services.relationships import configure_relationships
from resources.chat import (
    SendMessage,
    StartConversation,
    GetConversation,
    GetConversations,
)
from resources.roomate_request import (
    RoommateRequest,
    GetUnviewedRequests,
    MarkRequestsViewed,
    RoomateCheckRequest,
    GetAllRequests,
)

app = create_app()
users_online = set()

SWAGGER_URL = "/swagger"
API_URL = "/swagger.json"
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL, API_URL, config={"app_name": "Sample API"}
)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)


@app.route("/swagger.json")
def swagger():
    with open("swagger.json", "r") as f:
        return jsonify(json.load(f))


@socketio.on("connect")
def handle_connect():
    print("Client connected")


@socketio.on("disconnect")
def handle_disconnect():
    print("Client disconnected")


@socketio.on("join")
def handle_join(data):
    room = data["room"]
    join_room(room)
    emit("user_joined", {"room": room}, room=room)


@socketio.on("leave")
def handle_leave(data):
    room = data["room"]
    leave_room(room)
    emit("user_left", {"room": room}, room=room)

@socketio.on("user_connect")
def handle_connect(data):
    user_id = data["user_id"]
    if user_id:
        users_online.add(user_id)
        emit("update_user_list", list(users_online), broadcast=True)

@socketio.on("user_disconnect")
def handle_disconnect(data):
    user_id = data["user_id"]
    if user_id:
        users_online.discard(user_id)
        emit("update_user_list", list(users_online), broadcast=True)

@socketio.on("message")
def handle_message(data):
    room = data["room"]
    message_value = data["message"]
    author_id = data["author_id"]

    # Encrypt the message value
    encrypted_message_value = encrypt_message(message_value)

    # Save the encrypted message to the database
    new_message = Message(
        conversation_id=room, author_id=author_id, value=encrypted_message_value
    )
    db.session.add(new_message)
    db.session.commit()

    # Emit the message to all clients in the room with the original message value
    emit(
        "message",
        {
            "conversation_id": room,
            "author_id": author_id,
            "value": message_value,  # Sending the original message value, not encrypted
            "sent_at": new_message.sent_at.isoformat(),
        },
        room=room,
    )



if __name__ == "__main__":
    with app.app_context():
        import models
        db.create_all()
        configure_relationships()
    wsgi.server(eventlet.wrap_ssl(eventlet.listen(("127.0.0.1", 5000)),
                                  certfile=app.config['SSL_CERT_PATH'],
                                  keyfile=app.config['SSL_KEY_PATH']), app)

