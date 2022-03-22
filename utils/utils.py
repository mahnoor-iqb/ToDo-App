from flask import jsonify
from flask import request
import jwt
from functools import wraps
from models.user import User
from models.session import Session
from flask import current_app


def build_response(success, payload, error):
    return jsonify({'success': success, 'payload': payload, 'error': error})


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.cookies.get('access_token')
        if not token:
            return build_response(success=False, payload="", error="Access token not provided!")

        # Check if token exists in the database 
        sess = Session.query.filter_by(id=token).first()
        if not sess:
            return build_response(success=False, payload="", error="Invalid Session!")

        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'])
        except:
            return build_response(success=False, payload="", error="Invalid Token!")

        current_user = User.query.filter_by(id=data['user_id']).first()
        return f(current_user, *args, **kwargs)
    return decorated
