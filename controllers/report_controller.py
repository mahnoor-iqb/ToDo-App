from models.task import Task
from flask_sqlalchemy import SQLAlchemy
from utils.utils import build_response, token_required, is_same
from collections import defaultdict
import itertools
import logging


db = SQLAlchemy()

logger = logging.getLogger(__name__)

@token_required
def count_tasks(current_user):
    total_tasks = Task.query.filter_by(user_id=current_user.id).count()

    if not total_tasks:
        logger.error("No task found")
        return build_response(success=False, payload="", error="No task found")

    completed_tasks = Task.query.filter_by(
        completion_status=True).filter_by(user_id=current_user.id).count()
    remaining_tasks = Task.query.filter_by(
        completion_status=False).filter_by(user_id=current_user.id).count()

    return build_response(success=True, payload={
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'remaining_tasks': remaining_tasks
        }, error="")


@token_required
def get_average_tasks(current_user):
    result = Task.query.filter_by(completion_status=True).filter_by(
        user_id=current_user.id).all()

    if not result:
        logger.error("No completed task found")
        return build_response(success=False, payload="", error="No completed task found")

    groupby_date = defaultdict(list)

    for task in result:
        groupby_date[task.completion_date.date()].append(task)

    groupby_date = groupby_date.values()

    tasks_per_day = [len(tasks) for tasks in groupby_date]
    average_tasks = sum(tasks_per_day)/len(groupby_date)

    return build_response(success=True, payload={"average_tasks": average_tasks}, error="")


@token_required
def get_late_tasks(current_user):
    late_tasks = Task.query.filter(Task.user_id == current_user.id).filter(
        Task.completion_status == True).filter(Task.completion_date > Task.due_date).count()
    
    if not late_tasks:
        logger.error("No late task found")
        return build_response(success=False, payload="", error="No late tasks found")
    
    return build_response(success=True, payload={"late_tasks": late_tasks}, error="")


@token_required
def get_max_tasks_date(current_user):
    result = Task.query.filter_by(completion_status=True).filter_by(
        user_id=current_user.id).all()

    if not result:
        logger.error("No completed task found")
        return build_response(success=False, payload="", error="No completed task found")

    groupby_date = defaultdict(list)

    for task in result:
        groupby_date[task.completion_date.date()].append(task)

    tasks_per_day = {date: len(tasks)
                     for (date, tasks) in groupby_date.items()}

    max_tasks_date = max(tasks_per_day, key=tasks_per_day.get)

    return build_response(success=True, payload={"max_tasks_date": max_tasks_date}, error="")


@token_required
def get_weekly_tasks(current_user):
    tasks = Task.query.filter_by(user_id=current_user.id).all()

    if not tasks:
        logger.error("No task found")
        return build_response(success=False, payload= "", error="No task found")

    week_days = {'Monday':0, 'Tuesday':0, 'Wednesday':0, 'Thursday':0, 'Friday':0, 'Saturday':0, 'Sunday':0}

    for task in tasks:
        day = task.creation_date.strftime('%A')
        week_days[day] += 1

    return build_response(success=True, payload=week_days, error="")


@token_required
def get_similar_tasks(current_user):
    tasks = Task.query.filter_by(user_id=current_user.id).all()

    if not tasks:
        logger.error("No task found")
        return build_response(success=False, payload= "", error="No task found")

    similar_tasks = []
    if not tasks:
        return build_response(success=False, payload= "", error="No task found")

    for task1, task2 in itertools.combinations(tasks, 2):
        if is_same(task1.description, task2.description):
            similar_tasks.append([task1.id, task2.id])
    
    return build_response(success=True, payload= similar_tasks, error="")

