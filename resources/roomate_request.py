import logging

from flask import Flask, request
from flask_restful import Resource, Api
from db_app import db, socketio
from models.roomate_request import RoommateRequestModel
from models.student import StudentModel


class RoommateRequest(Resource):

    def post(self):
        # Create a new roommate request
        data = request.get_json()
        # Check if a request between these users already exists
        existing_request = RoommateRequestModel.query.filter_by(
            requester_id=data['requester_id'], target_id=data['target_id']
        ).first()
        if existing_request:
            # If a request exists, return a message without creating a new one
            return {'message': 'Roommate request already exists between these users'}, 409

        # If no existing request, create a new one
        new_request = RoommateRequestModel(requester_id=data['requester_id'], target_id=data['target_id'],
                                           accepted=None)
        db.session.add(new_request)
        db.session.commit()

        # Notify the target user via WebSocket
        socketio.emit('new_roommate_request', {'message': 'New roommate request!', 'target_id': data['target_id']},
                      room=f"user_{data['target_id']}")

        return {'message': 'Request created successfully'}, 201

    def delete(self, request_id):
        # Delete a roommate request
        request = RoommateRequestModel.query.get(request_id)
        if request:
            db.session.delete(request)
            db.session.commit()
            return {'message': 'Request deleted'}, 200
        else:
            return {'message': 'Request not found'}, 404

    # def patch(self, request_id):
    #     # Partially update a roommate request
    #     data = request.get_json()
    #     roommate_request = RoommateRequestModel.query.get(request_id)  # Renamed variable
    #     if roommate_request:
    #         if 'accepted' in data:
    #             roommate_request.accepted = data['accepted']  # Use the new variable name
    #         db.session.commit()
    #         return {'message': 'Request updated'}, 200
    #     else:
    #         return {'message': 'Request not found'}, 404

    def patch(self, request_id):
        data = request.get_json()
        roommate_request = RoommateRequestModel.query.get(request_id)
        if roommate_request:
            if 'accepted' in data:
                roommate_request.accepted = data['accepted']
                if data['accepted']:
                    # Update the requester and target id_status to "2" (matched)
                    requester = StudentModel.query.get(roommate_request.requester_id)
                    target = StudentModel.query.get(roommate_request.target_id)
                    if requester:
                        requester.id_status = 2
                    if target:
                        target.id_status = 2
                db.session.commit()
                return {'message': 'Request updated'}, 200
            else:
                return {'message': 'Invalid data'}, 400
        else:
            return {'message': 'Request not found'}, 404

    def get(self, target_id):
        # Fetch only the requests where 'target_id' matches the parameter
        requests = RoommateRequestModel.query.filter_by(target_id=target_id).all()
        data = []
        for req in requests:
            request_details = {
                "request_id": req.request_id,
                "requester_id": req.requester.id,
                "target_id": req.target.id,
                "requester_lastname": req.requester.lastname,
                "viewed": req.viewed,
                "requester_firstname": req.requester.firstname,
                "requester_status_id": req.requester.id_status,
                "requester_avatar": req.requester.avatar_link,
                "target_status_id": req.target.id_status,
                "accepted": req.accepted
            }
            data.append(request_details)

        return {'requests': data}, 200


class GetAllRequests(Resource):
    def get(self):
        # Get all roommate requests
        requests = RoommateRequestModel.query.all()
        return {'requests': [request.to_get_all_dict() for request in requests]}, 200


class GetUnviewedRequests(Resource):
    def get(self, user_id):
        requests = RoommateRequestModel.query.filter_by(target_id=user_id,
                                                        viewed=0).all()  # Assuming 'viewed' is a TINYINT
        return [req.to_dict() for req in requests], 200


class MarkRequestsViewed(Resource):
    def post(self):
        data = request.get_json()
        request_ids = data.get('request_ids', [])
        requests = RoommateRequestModel.query.filter(RoommateRequestModel.request_id.in_(request_ids)).all()
        for req in requests:
            req.viewed = 1  # Set viewed to 1 to mark as viewed
        db.session.commit()
        for req in requests:
            socketio.emit('request_viewed',
                          {'message': 'Your roommate request has been viewed', 'request_id': req.request_id},
                          room=f"user_{req.target_id}")

        return {'message': 'Requests marked as viewed'}, 200


# class RoomateCheckRequest(Resource):
#     def get(self, requester_id=None, target_id=None):
#         if requester_id and target_id:
#             # Check for specific roommate request between two users
#             existing_request = RoommateRequestModel.query.filter_by(
#                 requester_id=requester_id, target_id=target_id
#             ).first()
#             if existing_request:
#                 return {'exists': True, 'accepted': existing_request.accepted}, 200
#             return {'exists': False}, 200
#
#         # Get all roommate requests if no specific IDs are provided
#         requests = RoommateRequestModel.query.all()
#         return {'requests': [req.to_dict() for req in requests]}, 200

class RoomateCheckRequest(Resource):
    def get(self, requester_id=None, target_id=None):
        if requester_id and target_id:
            # Check for a specific roommate request between two users in either direction
            existing_request = RoommateRequestModel.query.filter(
                (RoommateRequestModel.requester_id == requester_id) & (RoommateRequestModel.target_id == target_id) |
                (RoommateRequestModel.requester_id == target_id) & (RoommateRequestModel.target_id == requester_id)
            ).first()
            if existing_request:
                return {'exists': True, 'accepted': existing_request.accepted}, 200
            return {'exists': False}, 200

        # Get all roommate requests if no specific IDs are provided
        requests = RoommateRequestModel.query.all()
        return {'requests': [req.to_dict() for req in requests]}, 200
