from db_app import db
from werkzeug.security import generate_password_hash, check_password_hash
import json


class UserModel(db.Model):
    __tablename__ = 'user'
    __table_args__ = {'schema': 'studmate'}

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    id_role = db.Column(db.Integer, nullable=False)

    def __init__(self, email=None, password=None, id_role=None):
        self.token = None

        if email is not None:
            self.email = email
        if password is not None:
            self.password = password
        if id_role is not None:
            self.id_role = id_role

    @property
    def serialize(self):
        """Return object data in a serializable format."""
        return {
            'id': self.id,
            'email': self.email,
            'id_role': self.id_role,
            'token': getattr(self, 'token', None),
        }

    @classmethod
    def get_user_by_email(cls, email):
        return cls.query.filter_by(email=email).first()

    def add_token(self, token):
        self.token = token

    def login(self, email, password):
        user = self.get_user_by_email(email)
        if not user or not check_password_hash(user.password, password):
            return
        user.password = None
        return user
