from flask import jsonify
from flask import request, session
import jwt
from functools import wraps
from models.user import User

def build_response(success, payload, error):
    return jsonify({'success': success, 'payload': payload, 'error': error})
