from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key = True)
    email = db.Column(db.String(100))
    password = db.Column(db.String(100))   
    admin = db.Column(db.Boolean)
    activated =  db.Column(db.Boolean)
    tasks = db.relationship('Task')
    session = db.relationship('Session')


    @property
    def serialize(self):
        return {
            'id': self.id,
            'email': self.email,
            'admin': self.admin,
            'activated': self.activated
        }