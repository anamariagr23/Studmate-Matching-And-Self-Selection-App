from werkzeug.security import check_password_hash

from models.student import StudentModel
from models.user import UserModel


class UserAuthenticationResponse:
    def __init__(self, user):
        self.user = user
        self.token = None
        self.details_completed = None
        self._fetch_student_details()

    def serialize(self):
        """Return object data in a serializable format."""
        data = {
            'id': self.user.id,
            'email': self.user.email,
            'id_role': self.user.id_role,
            'token': self.token,
        }
        if self.details_completed is not None:
            data['details_completed'] = self.details_completed
        return data

    def add_token(self, token):
        self.token = token

    @staticmethod
    def login(email, password):
        user = UserModel.get_user_by_email(email)
        if not user or not check_password_hash(user.password, password):
            return None
        return UserAuthenticationResponse(user)

    def _fetch_student_details(self):
        if self.user.is_student():
            student = StudentModel.query.filter_by(id=self.user.id).first()
            if student:
                self.details_completed = student.details_completed

