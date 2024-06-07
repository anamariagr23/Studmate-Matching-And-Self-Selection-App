# from flask_sqlalchemy import SQLAlchemy
# db = SQLAlchemy()

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO

db = SQLAlchemy()
socketio = SocketIO()


def create_app():
    app = Flask(__name__)
    # app.config.from_object('config.Config')

    app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:root@localhost/studmate"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    # TO DO figure out how to do this with environment variables later
    app.config["SECRET_KEY"] = "b'7P?DG/tX<siHk"

    db.init_app(app)
    socketio.init_app(app, cors_allowed_origins="*")

    return app

