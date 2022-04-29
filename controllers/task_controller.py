from flask import request, send_file
import datetime
from models.task import Task
from models.session import Session
from flask_sqlalchemy import SQLAlchemy
from utils.utils import build_response, token_required
import os
import logging
from config import basedir

db = SQLAlchemy()

logger = logging.getLogger(__name__)

"""Get all tasks from the database"""
@token_required
def show_all_tasks(current_user):  
    data = Task.query.filter_by(user_id=current_user.id)
    return build_response(success=True, payload=[i.serialize for i in data], error="")


"""Get task having the provided id from the database"""
@token_required
def show_task(current_user, task_id):
    task = Task.query.get(task_id)

    if not task:
        logger.error("Task does not exist")
        return build_response(success=False, payload="", error="Task doesn't exist!")

    if task.user_id != current_user.id:
        logger.error("Permission denied")
        return build_response(success=False, payload="", error="Permission Denied!")

    return build_response(success=True, payload=task.serialize, error="")


"""Add a task to the database"""
@token_required
def add_task(current_user):
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

    logger.info("New task added")
    return build_response(success=True, payload=task.serialize, error="")


"""Delete a task from the database"""
@token_required
def delete_task(current_user, task_id):
    task = Task.query.get(task_id)

    if not task:
        logger.error("Task does not exist")
        return build_response(success=False, payload="", error="Task doesn't exist!")

    if task.user_id != current_user.id:
        logger.error("Permission denied")
        return build_response(success=False, payload="", error="Permission Denied!")

    db.session.query(Task).filter(Task.id == task_id).delete()
    db.session.commit()

    logger.info(f"Task {task_id} deleted")
    return build_response(success=True, payload=f"Task {task_id} deleted", error="")


"""Find task with the provided id and update it"""
@token_required
def update_task(current_user, task_id):
    task = Task.query.filter_by(id=task_id).first()

    if not task:
        logger.error("Task does not exist")
        return build_response(success=False, payload="", error="Task doesn't exist!")

    if task.user_id != current_user.id:
        logger.error("Permission denied")
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

    logger.info(f"Task {task.id} updated")
    return build_response(success=True,payload=task.serialize, error="")


"""Store file attachment on the server"""
@token_required
def attach_file(current_user, task_id):
    task = Task.query.filter_by(id=task_id).first()

    if not task:
        logger.error("Task does not exist")
        return build_response(success=False, payload="", error="Task doesn't exist!")

    if task.user_id != current_user.id:
        logger.error("Permission denied")
        return build_response(success=False, payload="", error="Permission Denied!")

    file = request.files["file_attachment"]
    user_dir = os.path.join(basedir, f'Downloads/user{task.user_id}')

    if os.path.exists(user_dir):
        file.save(os.path.join(user_dir, file.filename))
    else:
        os.makedirs(user_dir)
        file.save(os.path.join(user_dir, file.filename))

    task.file_attachment =  file.filename

    db.session.merge(task)
    db.session.commit()

    logger.info(f"File {task.file_attachment} attached with task {task.id}")
    return build_response(success=True, payload=task.serialize, error="")


"""Download file attachment from the server"""
@token_required
def download_file(current_user, task_id):
    task = Task.query.get(task_id)

    if not task:
        logger.error("Task doesn't exist")
        return build_response(success=False, payload="", error="Task doesn't exist!")

    if task.user_id != current_user.id:
        logger.error("Permission denied")
        return build_response(success=False, payload="", error="Permission Denied!")

    user_dir = os.path.join(basedir, f'Downloads/user{task.user_id}')

    logger.info("File download successful")
    return send_file(user_dir+ "/"+task.file_attachment, as_attachment=True)
