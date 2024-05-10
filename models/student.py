from db_app import db
from models.user import UserModel
from models.status import StatusModel
from models.sex import SexModel


class StudentModel(db.Model):
    __tablename__ = 'student'
    __table_args__ = {'schema': 'studmate'}

    id = db.Column(db.Integer, db.ForeignKey('studmate.user.id'), primary_key=True)
    lastname = db.Column(db.String(255))
    firstname = db.Column(db.String(255))
    id_status = db.Column(db.Integer, db.ForeignKey('studmate.status.id'), nullable=True)
    id_major = db.Column(db.Integer, db.ForeignKey('studmate.major.id'), nullable=True)
    is_blocked = db.Column(db.Boolean, nullable=True)
    id_sex = db.Column(db.Integer, nullable=True)
    description = db.Column(db.String(255))
    details_completed = db.Column(db.Boolean, nullable=False)
    avatar_link = db.Column(db.String(500))
    year_of_study = db.Column(db.Integer, nullable=True)

    user = db.relationship(UserModel, backref='student', uselist=False)
