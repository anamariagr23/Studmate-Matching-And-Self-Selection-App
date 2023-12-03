from db_app import db
from werkzeug.security import generate_password_hash, check_password_hash


class UserModel(db.Model):
    __tablename__ = 'user'
    __table_args__ = {'schema': 'studmate'}

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    id_role = db.Column(db.Integer, nullable=False)

    def get_user_by_email(self, email):
        user = db.users.find_one({"email": email, "active": True})
        if not user:
            return
        user["_id"] = str(user["_id"])
        return user

    def login(self, email, password):
        user = self.get_user_by_email(email)
        if not user or not check_password_hash(user["password"], password):
            return
        user.pop("password")
        return user

    def __repr__(self):
        return f'<User {self.email}>'
