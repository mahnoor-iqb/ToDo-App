from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key = True)
    email = db.Column(db.String(100))
    password = db.Column(db.String(100))   
    admin = db.Column(db.Boolean)
    activated =  db.Column(db.Boolean)
    oauth = db.Column(db.Boolean)
    tasks = db.relationship('Task')
    session = db.relationship('Session')
    
    def __init__(self, email, password, admin = False, activated = False, oauth = False):
        if password is not None:
            self.password = generate_password_hash(password, method='sha256')
        self.email = email
        self.admin = admin
        self.activated = activated
        self.oauth = oauth


    @property
    def serialize(self):
        return {
            'id': self.id,
            'email': self.email,
            'admin': self.admin,
            'activated': self.activated,
            'oauth': self.oauth
        }