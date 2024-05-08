from db_app import db

class CategoryModel(db.Model):
    __tablename__ = 'description_category'
    __table_args__ = {'schema': 'studmate'}

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)

    # Relationship backref from CategoryStudentSelfDescriptionModel
    descriptions = db.relationship('CategoryStudentSelfDescriptionModel', backref='category', lazy='dynamic')
