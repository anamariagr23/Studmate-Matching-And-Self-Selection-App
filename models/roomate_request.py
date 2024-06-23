from db_app import db


class RoommateRequestModel(db.Model):
    __tablename__ = 'roommate_requests'
    __table_args__ = {'schema': 'studmate'}

    request_id = db.Column(db.Integer, primary_key=True)
    requester_id = db.Column(db.Integer, db.ForeignKey('studmate.student.id'), nullable=False)
    target_id = db.Column(db.Integer, db.ForeignKey('studmate.student.id'), nullable=False)
    accepted = db.Column(db.Boolean, nullable=False)
    request_date = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())
    viewed = db.Column(db.Boolean, default=False)  # Indicates if the request has been viewed

    # Relationships
    requester = db.relationship('StudentModel', foreign_keys=[requester_id],
                                backref=db.backref('requests_made', lazy='dynamic'))
    target = db.relationship('StudentModel', foreign_keys=[target_id],
                             backref=db.backref('requests_received', lazy='dynamic'))

    def to_dict(self):
        return {
            "request_id": self.request_id,
            "requester_id": self.requester_id,
            "target_id": self.target_id,
            "accepted": self.accepted,
            "request_date": self.request_date.isoformat() if self.request_date else None,
            "viewed": self.viewed
        }

    def to_get_all_dict(self):
        return {
            "request_id": self.request_id,
            "requester_id": self.requester_id,
            "requester_firstname": self.requester.firstname,
            "requester_lastname": self.requester.lastname,
            "requester_avatar": self.requester.avatar_link,
            "target_id": self.target_id,
            "target_firstname": self.target.firstname,
            "target_lastname": self.target.lastname,
            "target_avatar": self.target.avatar_link,
            "accepted": self.accepted,
            "request_date": self.request_date.isoformat() if self.request_date else None,
        }
