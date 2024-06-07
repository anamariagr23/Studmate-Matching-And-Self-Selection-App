from db_app import db

class ConversationUser(db.Model):
    __tablename__ = 'conversation_user'
    __table_args__ = {'schema': 'studmate'}

    conversation_id = db.Column(db.Integer, db.ForeignKey('studmate.conversation.id'), primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('studmate.student.id'), primary_key=True)
