from lib2to3.pgen2 import token
from flask import request

from models.user import User
from models.session import Session
from utils.utils import build_response, token_required
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash

db = SQLAlchemy()

"""Get all users from the database"""
@token_required
def show_all_users(current_user):
    if not current_user.admin:
        return build_response(success=False, payload="", error="Permission Denied")

    data = User.query.all()
    return build_response(success=True, payload=[i.serialize for i in data], error="")


"""Get user with the provided id from the database"""
@token_required
def show_user(current_user, user_id):
    if not current_user.admin:
        return build_response(success=False, payload="", error="Permission Denied")
    user = User.query.get(user_id)
    return build_response(success=True, payload=user.serialize, error="")


"""Delete a user from the database"""
@token_required
def delete_user(current_user, user_id):
    if not current_user.admin:
        return build_response(success=False, payload="", error="Permission Denied")
    db.session.query(User).filter(User.id == user_id).delete()
    db.session.commit()
    return build_response(success=True, payload=f"User {user_id} deleted", error="")


"""Find user with the provided id and update record"""
@token_required
def update_user(current_user):
    user = User.query.filter_by(id=current_user.id).first()

    if user.id != current_user.id:
        return build_response(success=False, payload="", error="Permission Denied!")

    email = request.json["email"]
    hashed_password = generate_password_hash(
    request.json['password'], method='sha256')

    user.email = email
    user.password = hashed_password

    db.session.merge(user)
    db.session.commit()

    return build_response(success=True, payload= user.serialize, error="")