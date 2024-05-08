from db_app import db


class CategoryStudentSelfDescriptionModel(db.Model):
    __tablename__ = 'category_student_self_description'
    __table_args__ = {'schema': 'studmate'}

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('studmate.student.id'))
    category_id = db.Column(db.Integer, db.ForeignKey('studmate.description_category.id'))
    answer = db.Column(db.Text)
    importance_score = db.Column(db.Integer, db.CheckConstraint('importance_score BETWEEN 1 AND 10'))
