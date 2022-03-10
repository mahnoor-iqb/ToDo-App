from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from models.user import db

class Task(db.Model):
    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(100))
    description = db.Column(db.String(500))

    creation_date = db.Column(db.DateTime(timezone = True), default = datetime.utcnow)
    due_date = db.Column(db.DateTime(timezone = True))
    completion_date = db.Column(db.DateTime(timezone = True))
    completion_status = db.Column(db.Boolean)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    @property
    def serialize(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'creation_date': self.creation_date,
            'due_date': self.due_date,
            'completion_date': self.completion_date,
            'completion_status': self.completion_status,
            'user_id': self.user_id,

        }

