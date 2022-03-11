
from flask import request, jsonify

from models.user import User
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def show_all():
    data = User.query.all()
    return jsonify(json_list=[i.serialize for i in data])


def show(user_id):
    user = User.query.get(user_id)
    return jsonify(user.serialize)


def add():
    name = request.json["name"]
    email = request.json["email"]
    password = request.json["password"]

    user = User(name=name, email=email, password=password)
    db.session.add(user)
    db.session.commit()

    return jsonify({
        "name": name,
        "email": email,
        "password": password
    })
