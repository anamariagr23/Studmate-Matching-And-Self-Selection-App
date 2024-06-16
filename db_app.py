


import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from dotenv import load_dotenv
from cryptography.fernet import Fernet

db = SQLAlchemy()
socketio = SocketIO()

def create_app():
    # Load environment variables from .env file
    load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))

    app = Flask(__name__)
    app.config.from_object('config.Config')

    db.init_app(app)
    socketio.init_app(app, cors_allowed_origins="*")

    return app

