from flask import request, jsonify
import datetime
from models.task import Task
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def show():
    data = Task.query.all()
    return jsonify(json_list=[i.serialize for i in data])


def add():
    title = request.form["title"]
    description = request.form["description"]

    creation_date = datetime.datetime.strptime(request.form["creation_date"], '%Y-%m-%d %H:%M:%S')
    due_date = datetime.datetime.strptime(request.form["creation_date"], '%Y-%m-%d %H:%M:%S')
    completion_date = datetime.datetime.strptime(request.form["creation_date"], '%Y-%m-%d %H:%M:%S')

    completion_status = int(request.form["completion_status"])
    user_id= int(request.form["user_id"])


    task = Task(title=title, 
    description=description, 
    creation_date=creation_date, 
    due_date=due_date,
    completion_date=completion_date, 
    completion_status=completion_status, 
    user_id=user_id)

    db.session.add(task)
    db.session.commit()

    return jsonify({
        "title": title,
        "description": description,
        "creation_date": creation_date,
        "due_date": due_date,
        "completion_date": completion_date,
        "completion_status": completion_status,
        "user_id": user_id
    })

