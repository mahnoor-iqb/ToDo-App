from flask import request, jsonify
import datetime
from models.task import Task
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def show_all():
    data = Task.query.all()
    return jsonify(json_list=[i.serialize for i in data])


def show(task_id):
    task = Task.query.get(task_id)
    return jsonify(task.serialize)


def add():
    title = request.json["title"]
    description = request.json["description"]

    creation_date = datetime.datetime.strptime(
        request.json["creation_date"], '%Y-%m-%d %H:%M:%S')
    due_date = datetime.datetime.strptime(
        request.json["due_date"], '%Y-%m-%d %H:%M:%S')
    completion_date = datetime.datetime.strptime(
        request.json["completion_date"], '%Y-%m-%d %H:%M:%S')

    completion_status = int(request.json["completion_status"])
    user_id = int(request.json["user_id"])

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


def delete(task_id):
    db.session.query(Task).filter(Task.id == task_id).delete()
    db.session.commit()
    return f"Task {task_id} has been deleted."


def update(task_id):
    task = Task.query.filter_by(id=task_id).first()

    title = request.json["title"]
    description = request.json["description"]
    creation_date = datetime.datetime.strptime(
        request.json["creation_date"], '%Y-%m-%d %H:%M:%S')
    due_date = datetime.datetime.strptime(
        request.json["due_date"], '%Y-%m-%d %H:%M:%S')
    completion_date = datetime.datetime.strptime(
        request.json["completion_date"], '%Y-%m-%d %H:%M:%S')
    completion_status = int(request.json["completion_status"])
    user_id = int(request.json["user_id"])

    task.title = title
    task.description = description
    task.creation_date = creation_date
    task.due_date = due_date
    task.completion_status = completion_status
    task.completion_date = completion_date
    task.user_id = user_id

    db.session.merge(task)
    db.session.commit()

    return jsonify({
        "title": task.title,
        "description": task.description,
        "creation_date": task.creation_date,
        "due_date": task.due_date,
        "completion_date": task.completion_date,
        "completion_status": task.completion_status,
        "user_id": task.user_id
    })
