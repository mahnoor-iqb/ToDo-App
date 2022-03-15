
from flask import request

from models.user import User
from utils.utils import build_response
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash
from flask_login import login_required, current_user
db = SQLAlchemy()


"""
Get all users from the database
"""

@login_required
def show_all_users():
    if not current_user.admin:
        return build_response(success=True, payload="", error="Permission Denied")

    data = User.query.all()
    return build_response(success=True, payload=[i.serialize for i in data], error="")


"""
Get user with the provided id from the database
"""

@login_required
def show_user(user_id):
    if not current_user.admin:
        return build_response(success=True, payload="", error="Permission Denied")
    user = User.query.get(user_id)
    return build_response(success=True, payload=user.serialize, error="")


"""
Add a user to the database
"""

@login_required
def add_user():
    if not current_user.admin:
        return build_response(success=True, payload="", error="Permission Denied")
    email = request.json["email"]
    hashed_password = generate_password_hash(
    request.form['password'], method='sha256')
    user = User(email=email, password=hashed_password)
    db.session.add(user)
    db.session.commit()

    added_user = {
        "email": email,
        "password": hashed_password
    }

    return build_response(success=True, payload=added_user, error="")


"""
Delete a user from the database
"""
@login_required
def delete_user(user_id):
    if not current_user.admin:
        return build_response(success=True, payload="", error="Permission Denied")
    db.session.query(User).filter(User.id == user_id).delete()
    db.session.commit()
    return build_response(success=True, payload=f"User {user_id} deleted", error="")


"""
Find user with the provided id and update record
"""

@login_required
def update_user():
    user = User.query.filter_by(id=current_user.id).first()

    if user.id != current_user.id:
        return build_response(success=False, payload="", error="Permission Denied!")

    email = request.json["email"]
    password = request.json["password"]

    user.email = email
    user.password = password

    db.session.merge(user)
    db.session.commit()

    updated_user = {
        "email": email,
        "password": password
    }

    return build_response(success=True, payload=updated_user, error="")
