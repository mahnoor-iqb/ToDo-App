from flask import jsonify
from flask import request
import jwt
from functools import wraps
from models.user import User
from models.session import Session
from flask import current_app
import logging


logger = logging.getLogger(__name__)

def build_response(success, payload, error):
    return jsonify({'success': success, 'payload': payload, 'error': error})


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.cookies.get('access_token')
        if not token:
            logger.error("Access token not provided")
            return build_response(success=False, payload="", error="Access token not provided!")

        # Check if token exists in the database 
        sess = Session.query.filter_by(id=token).first()
        if not sess:
            logger.error("Invalid session")
            return build_response(success=False, payload="", error="Invalid session!")

        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'])
        except:
            logger.error("Invalid login token")
            return build_response(success=False, payload="", error="Invalid Token!")

        current_user = User.query.filter_by(id=data['user_id']).first()
        return f(current_user, *args, **kwargs)
    return decorated


def is_same(a,b):
    a= a.lower().split(" ")
    b = b.lower().split(" ")
    return set(a)<=set(b) or set(b)<=set(a)