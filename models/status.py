from db_app import db


class StatusModel(db.Model):
    __tablename__ = 'status'
    __table_args__ = {'schema': 'studmate'}

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f'<StatusModel(id={self.id}, name={self.name})>'
