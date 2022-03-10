
from flask import request, jsonify

from models.user import User
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def show():
    data = User.query.all()
    return jsonify(json_list=[i.serialize for i in data])

def add():
    name = request.form["name"]
    email = request.form["email"]
    password = request.form["password"]

    user = User(name=name, email=email, password=password)
    db.session.add(user)
    db.session.commit()

    return jsonify({
        "name": name,
        "email": email,
        "password": password
    })
