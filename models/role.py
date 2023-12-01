from db_app import db

class RoleModel(db.Model):
    __tablename__ = 'role'
    __table_args__ = {'schema': 'studmate'}

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f'<Role {self.name}>'