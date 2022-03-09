from . import db, app
from datetime import datetime

# Task Schema
class Task(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(100))
    description = db.Column(db.String(500))
    creation_date = db.Column(db.DateTime(timezone = True), default = datetime.utcnow)
    due_date = db.Column(db.DateTime(timezone = True))
    completion_date = db.Column(db.DateTime(timezone = True))
    completion_status = db.Column(db.Boolean)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

