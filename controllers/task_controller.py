from flask import request, send_from_directory
import datetime
from models.task import Task
from flask_sqlalchemy import SQLAlchemy
from utils.utils import build_response
from flask_login import current_user, login_required
import os

db = SQLAlchemy()


"""
Get all tasks from the database
"""

@login_required
def show_all_tasks():
    data = Task.query.filter_by(user_id=current_user.id)
    return build_response(success=True, payload=[i.serialize for i in data], error="")


"""
Get task having the provided id from the database
"""

@login_required
def show_task(task_id):
    task = Task.query.get(task_id)

    if not task:
        return build_response(success=False, payload="", error="Task doesn't exist!")

    if task.user_id != current_user.id:
        return build_response(success=False, payload="", error="Permission Denied!")
    return build_response(success=True, payload=task.serialize, error="")


"""
Add a task to the database
"""

@login_required
def add_task():
    title = request.json["title"]
    description = request.json["description"]

    # if task not completed yet
    if request.json.get("completion_date") is None:
        completion_date = None
    else: 
        completion_date = datetime.datetime.strptime(
        request.json["completion_date"], '%Y-%m-%d %H:%M:%S')

    creation_date = datetime.datetime.strptime(
        request.json["creation_date"], '%Y-%m-%d %H:%M:%S') 
    due_date = datetime.datetime.strptime(
        request.json["due_date"], '%Y-%m-%d %H:%M:%S')


    completion_status = int(request.json["completion_status"])

    task = Task(title=title,
                description=description,
                creation_date=creation_date,
                due_date=due_date,
                completion_date=completion_date,
                completion_status=completion_status,
                user_id=current_user.id)

    db.session.add(task)
    db.session.commit()

    added_task = {
        "title": title,
        "description": description,
        "creation_date": creation_date,
        "due_date": due_date,
        "completion_date": completion_date,
        "completion_status": completion_status,
        "user_id": current_user.id
    }

    return build_response(success=True, payload=added_task, error="")


"""
Delete a task from the database
"""

@login_required
def delete_task(task_id):
    task = Task.query.get(task_id)

    if not task:
        return build_response(success=False, payload="", error="Task doesn't exist!")

    if task.user_id != current_user.id:
        return build_response(success=False, payload="", error="Permission Denied!")

    db.session.query(Task).filter(Task.id == task_id).delete()
    db.session.commit()

    return build_response(success=True, payload=f"Task {task_id} deleted", error="")


"""
Find task with the provided id and update it
"""

@login_required
def update_task(task_id):
    task = Task.query.filter_by(id=task_id).first()

    if not task:
        return build_response(success=False, payload="", error="Task doesn't exist!")

    if task.user_id != current_user.id:
        return build_response(success=False, payload="", error="Permission Denied!")

    title = request.json["title"]
    description = request.json["description"]
    creation_date = datetime.datetime.strptime(
        request.json["creation_date"], '%Y-%m-%d %H:%M:%S')
    due_date = datetime.datetime.strptime(
        request.json["due_date"], '%Y-%m-%d %H:%M:%S')
    completion_date = datetime.datetime.strptime(
        request.json["completion_date"], '%Y-%m-%d %H:%M:%S')
    completion_status = int(request.json["completion_status"])

    task.title = title
    task.description = description
    task.creation_date = creation_date
    task.due_date = due_date
    task.completion_status = completion_status
    task.completion_date = completion_date

    db.session.merge(task)
    db.session.commit()

    updated_task = {
        "title": task.title,
        "description": task.description,
        "file_attachment": task.file_attachment,
        "creation_date": task.creation_date,
        "due_date": task.due_date,
        "completion_date": task.completion_date,
        "completion_status": task.completion_status,
        "user_id": task.user_id
    }

    return build_response(success=True, payload=updated_task, error="")


"""
Store file attachment on the server
"""

@login_required
def attach_file(task_id):
    task = Task.query.filter_by(id=task_id).first()

    if not task:
        return build_response(success=False, payload="", error="Task doesn't exist!")

    if task.user_id != current_user.id:
        return build_response(success=False, payload="", error="Permission Denied!")

    file = request.files["file_attachment"]
    user_dir = "/home/emumba/Desktop/ToDo-App/Downloads/user"+str(task.user_id)

    if os.path.exists(user_dir):
        file.save(os.path.join(user_dir, file.filename))
    else:
        os.makedirs(user_dir)
        file.save(os.path.join(user_dir, file.filename))

    task.file_attachment =  file.filename

    db.session.merge(task)
    db.session.commit()

    updated_task = {
        "title": task.title,
        "description": task.description,
        "file_attachment": task.file_attachment,
        "due_date": task.due_date,
        "creation_date": task.creation_date,
        "due_date": task.due_date,
        "completion_date": task.completion_date,
        "completion_status": task.completion_status,
        "user_id": task.user_id
    }

    return build_response(success=True, payload=updated_task, error="")

"""
Download file attachment from the server
"""

@login_required
def download_file(task_id):
    task = Task.query.get(task_id)

    if not task:
        return build_response(success=False, payload="", error="Task doesn't exist!")

    if task.user_id != current_user.id:
        return build_response(success=False, payload="", error="Permission Denied!")

    user_dir = "/home/emumba/Desktop/ToDo-App/Downloads/user"+str(task.user_id)
    return send_from_directory(user_dir, task.file_attachment)
