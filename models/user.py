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

    @classmethod
    def get_user_by_email(cls, email):
        return cls.query.filter_by(email=email).first()

    def is_student(self):
        return self.id_role == 3