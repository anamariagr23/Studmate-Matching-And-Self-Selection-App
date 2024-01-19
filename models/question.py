from db_app import db

class QuestionModel(db.Model):
    __tablename__ = 'question'
    __table_args__ = {'schema': 'studmate'}

    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(255), nullable=False)
    id_survey = db.Column(db.Integer, db.ForeignKey('survey.id'), nullable=False)
    multiple_choice = db.Column(db.Boolean, nullable=False, default=False)

    # Relationship to AnswerChoice
    answer_choices = db.relationship('AnswerChoiceModel', backref='question', lazy=True)
