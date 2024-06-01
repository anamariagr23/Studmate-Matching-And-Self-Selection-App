from db_app import db


class AnswerChoiceModel(db.Model):
    __tablename__ = 'answer_choice'
    __table_args__ = {'schema': 'studmate'}

    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    description = db.Column(db.String(255), nullable=False)
