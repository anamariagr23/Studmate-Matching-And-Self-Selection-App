from db_app import db


class MajorModel(db.Model):
    __tablename__ = 'major'
    __table_args__ = {'schema': 'studmate'}

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f'<MajorModel(id={self.id}, name={self.name})>'
