
from flask import request, jsonify, current_app
from flask_restful import Resource
from db_app import db, socketio
from models.conversation import Conversation
from models.conversation_user import ConversationUser
from models.message import Message
from models.student import StudentModel
import jwt

class SendMessage(Resource):
    def post(self):
        data = request.json
        conversation_id = data.get("conversation_id")
        author_id = data.get("author_id")
        value = data.get("value")
        parent_message_id = data.get("parent_message_id")

        message = Message(
            conversation_id=conversation_id,
            author_id=author_id,
            value=value,
            parent_message_id=parent_message_id
        )

        db.session.add(message)
        db.session.commit()

        socketio.emit("receive_message", {
            "conversation_id": conversation_id,
            "author_id": author_id,
            "value": value,
            "parent_message_id": parent_message_id,
            "sent_at": message.sent_at.isoformat(),
            "edited_at": message.edited_at.isoformat()
        })

        return {"status": "Message sent"}, 200

class StartConversation(Resource):
    def post(self):
        data = request.json
        user_ids = data.get("user_ids")

        conversation = Conversation()
        db.session.add(conversation)
        db.session.commit()

        for user_id in user_ids:
            conversation_user = ConversationUser(conversation_id=conversation.id, student_id=user_id)
            db.session.add(conversation_user)

        db.session.commit()

        return {"conversation_id": conversation.id}, 201

class GetConversation(Resource):
    def get(self, conversation_id):
        conversation = Conversation.query.get_or_404(conversation_id)
        messages = Message.query.filter_by(conversation_id=conversation_id).all()
        return {
            "conversation_id": conversation.id,
            "created_at": conversation.created_at.isoformat(),
            "updated_at": conversation.updated_at.isoformat(),
            "messages": [{"id": m.id, "author_id": m.author_id, "value": m.value,
                          "parent_message_id": m.parent_message_id,
                          "sent_at": m.sent_at.isoformat(), "edited_at": m.edited_at.isoformat()}
                         for m in messages]
        }


class GetConversations(Resource):
    def get(self):
        if "Authorization" in request.headers:
            token = request.headers["Authorization"].split(" ")[1]
            decoded_token = jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])

            current_user_id = decoded_token['id']

            current_student = StudentModel.query.filter_by(id=current_user_id).first()
            if not current_student:
                return {"message": "Student not found"}, 404

            dorm_id = current_student.dorm_id
            sex_id = current_student.id_sex

            students = StudentModel.query.filter_by(dorm_id=dorm_id, id_sex=sex_id, details_completed=True).all()
            students_data = []
            for student in students:
                if student.id == current_user_id:
                    continue

                conversation_user = ConversationUser.query.filter_by(student_id=student.id).first()
                conversation = None
                last_message = None

                if conversation_user:
                    conversation = Conversation.query.filter_by(id=conversation_user.conversation_id).order_by(Conversation.created_at.desc()).first()
                    last_message = Message.query.filter_by(conversation_id=conversation.id).order_by(Message.sent_at.desc()).first()

                conversation_student_info = {
                    'id': student.id,
                    'lastname': student.lastname,
                    'firstname': student.firstname,
                    'id_status': student.id_status,
                    'is_blocked': student.is_blocked,
                    'avatar_link': student.avatar_link,
                    'conversation_id': conversation.id if conversation else None,
                    'last_message': {
                        'id': last_message.id,
                        'author_id': last_message.author_id,
                        'value': last_message.value,
                        'sent_at': last_message.sent_at.isoformat()
                    } if last_message else None,

                }
                students_data.append(conversation_student_info)

            return {'conversation_summary': students_data}, 200
        else:
            return {'message': 'Access token not found'}, 400