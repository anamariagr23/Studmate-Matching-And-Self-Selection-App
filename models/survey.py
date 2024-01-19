from db_app import db

class SurveyModel(db.Model):
    __tablename__ = 'survey'
    __table_args__ = {'schema': 'studmate'}

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)

    # Relationship to Question
    questions = db.relationship('QuestionModel', backref='survey', lazy=True)
