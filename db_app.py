import os
from flask import Flask
from flask_cors import CORS
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from dotenv import load_dotenv
from cryptography.fernet import Fernet
from sqlalchemy import text

db = SQLAlchemy()
socketio = SocketIO()


def create_app(config_class='config.Config'):
    # Load environment variables from .env file
    load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))

    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    socketio.init_app(app, cors_allowed_origins="*")
    api = Api(app)
    CORS(app, supports_credentials=True, methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
         allow_headers=["Content-Type", "Authorization"])

    from resources.login import Login
    from resources.user import User
    from resources.role import Role
    from resources.student import Student
    from resources.major import Major
    from resources.dorm import Dorm
    from resources.sex import Sex
    from resources.google_login import GoogleLogin
    from resources.student_matches import StudentMatches
    from resources.student_profile import StudentProfile
    from services.encryption_util import encrypt_message
    from services.relationships import configure_relationships
    from resources.chat import SendMessage, StartConversation, GetConversation, GetConversations
    from resources.roomate_request import RoommateRequest, GetUnviewedRequests, MarkRequestsViewed, RoomateCheckRequest
    from resources.roomate_request import GetAllRequests
    from resources.student import StudentCategories

    api.add_resource(User, '/users')
    api.add_resource(Role, '/role')
    api.add_resource(Student, '/students')
    api.add_resource(Major, '/majors')
    api.add_resource(Dorm, '/dorms')
    api.add_resource(Sex, '/sexes')
    api.add_resource(Login, '/login', resource_class_kwargs={'secret_key': app.config['SECRET_KEY']})
    api.add_resource(GoogleLogin, '/google-login', resource_class_kwargs={'secret_key': app.config['SECRET_KEY']})
    api.add_resource(StudentProfile, '/student/<int:student_id>',
                     resource_class_kwargs={'secret_key': app.config['SECRET_KEY']})
    api.add_resource(StudentMatches, '/student-matches', resource_class_kwargs={'secret_key': app.config['SECRET_KEY']})
    api.add_resource(SendMessage, '/send-message')
    api.add_resource(StartConversation, '/start-conversation')
    api.add_resource(GetConversation, '/get-conversation/<int:user_id>')
    api.add_resource(GetConversations, '/get-conversations')
    api.add_resource(RoommateRequest, '/roommate_requests', '/roommate_requests/<int:request_id>',
                     '/roommate_requests/target/<int:target_id>')
    api.add_resource(GetUnviewedRequests, '/get_unviewed_requests/<int:user_id>')
    api.add_resource(MarkRequestsViewed, '/mark_requests_viewed')
    api.add_resource(RoomateCheckRequest, '/check_request/<int:requester_id>/<int:target_id>')
    api.add_resource(GetAllRequests, '/roommate_requests_all')
    api.add_resource(StudentCategories, '/student')

    with app.app_context():
        from models.survey import SurveyModel
        from models.question import QuestionModel
        from models.answer_choice import AnswerChoiceModel
        from models.category_student_self_description import CategoryStudentSelfDescriptionModel
        from models.category import CategoryModel
        from models.conversation_user import ConversationUser
        from models.conversation import Conversation
        from models.dorm import DormModel
        from models.major import MajorModel
        from models.message import Message
        from models.role import RoleModel
        from models.roomate_request import RoommateRequestModel
        from models.sex import SexModel
        from models.status import StatusModel
        from models.student import StudentModel
        from models.user import UserModel
        from models.user_authentication_response import UserAuthenticationResponse

        if config_class == 'config.TestConfig':
            db.session.execute(text("ATTACH DATABASE ':memory:' AS studmate"))

        db.create_all()

    return app

