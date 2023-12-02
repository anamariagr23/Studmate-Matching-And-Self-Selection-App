from db_app import db


class SexModel(db.Model):
    __tablename__ = 'sex'
    __table_args__ = {'schema': 'studmate'}

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)

    # students = db.relationship('StudentModel', backref='status', lazy=True)

    def __repr__(self):
        return f'<SexModel(id={self.id}, name={self.name})>'
