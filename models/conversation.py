from db_app import db
from sqlalchemy.sql import func


class Conversation(db.Model):
    __tablename__ = 'conversation'
    __table_args__ = {'schema': 'studmate'}

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, server_default=func.now())
    updated_at = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now())
    users = db.relationship('ConversationUser', backref='conversation', lazy=True)
    messages = db.relationship('Message', backref='conversation', lazy=True)
