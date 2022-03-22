from models.user import db

class Session(db.Model):
    __tablename__ = 'sessions'

    id = db.Column(db.String, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    @property
    def serialize(self):
        return {
            'id': self.id,
            'user_id': self.user_id
        }