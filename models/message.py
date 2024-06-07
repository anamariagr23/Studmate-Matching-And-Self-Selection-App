from db_app import db
from sqlalchemy.sql import func


class Message(db.Model):

    __tablename__ = 'message'
    __table_args__ = {'schema': 'studmate'}

    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('studmate.conversation.id'), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('studmate.student.id'), nullable=False)
    value = db.Column(db.Text, nullable=False)
    parent_message_id = db.Column(db.Integer, db.ForeignKey('studmate.message.id'), nullable=True)
    sent_at = db.Column(db.DateTime, server_default=func.now())
    edited_at = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now())
    parent_message = db.relationship('Message', remote_side=[id])
