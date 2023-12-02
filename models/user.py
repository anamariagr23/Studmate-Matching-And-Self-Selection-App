from db_app import db

class UserModel(db.Model):
    __tablename__ = 'user'
    __table_args__ = {'schema': 'studmate'}

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    id_role = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f'<User {self.email}>'