from models.task import Task
from flask_sqlalchemy import SQLAlchemy
from utils.utils import build_response, token_required, is_same
from datetime import datetime, timedelta
from collections import defaultdict
import itertools
import logging


db = SQLAlchemy()

logger = logging.getLogger(__name__)

cache = {}


def get_from_cache(user, report):
    if cache.get(user):
        if cache.get(user).get(report):
            if datetime.now() - cache[user][report][1] > timedelta(minutes=5):
                logger.info("Cache report expired")
                del cache[user][report]
                return

            logger.info("Getting from Cache")
            return cache[user][report][0]


def store_in_cache(user, report, data):
    if user in cache:
        cache[user][report] = [data, datetime.now()]
    else:
        cache[user] = {report: [data, datetime.now()]}

    logger.info("Storing in Cache")


@token_required
def count_tasks(current_user):
    cached_report = get_from_cache(current_user.id, "task_count")

    if cached_report:
        return build_response(success=True, payload=cached_report, error="")

    total_tasks = Task.query.filter_by(user_id=current_user.id).count()

    if not total_tasks:
        logger.error("No task found")
        return build_response(success=False, payload="", error="No task found")

    completed_tasks = Task.query.filter_by(
        completion_status=True).filter_by(user_id=current_user.id).count()
    remaining_tasks = Task.query.filter_by(
        completion_status=False).filter_by(user_id=current_user.id).count()

    data = {
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'remaining_tasks': remaining_tasks
    }

    store_in_cache(current_user.id, "task_count", data)

    return build_response(success=True, payload=data, error="")


@token_required
def get_average_tasks(current_user):
    cached_report = get_from_cache(current_user.id, "average_tasks")

    if cached_report:
        return build_response(success=True, payload={"average_tasks": cached_report}, error="")

    tasks = Task.query.filter_by(completion_status=True).filter_by(
        user_id=current_user.id).all()

    if not tasks:
        logger.error("No completed task found")
        return build_response(success=False, payload="", error="No completed task found")

    unique_completion_dates = len(set([task.completion_date.date() for task in tasks]))
    average_tasks = len(tasks)/unique_completion_dates

    store_in_cache(current_user.id, "average_tasks", average_tasks)

    return build_response(success=True, payload={"average_tasks": average_tasks}, error="")


@token_required
def get_late_tasks(current_user):
    cached_report = get_from_cache(current_user.id, "late_tasks")

    if cached_report:
        return build_response(success=True, payload={"late_tasks": cached_report}, error="")

    late_tasks = Task.query.filter(Task.user_id == current_user.id).filter(
        Task.completion_status == True).filter(Task.completion_date > Task.due_date).count()

    if not late_tasks:
        logger.error("No late task found")
        return build_response(success=False, payload="", error="No late tasks found")

    store_in_cache(current_user.id, "late_tasks", late_tasks)

    return build_response(success=True, payload={"late_tasks": late_tasks}, error="")


@token_required
def get_max_tasks_date(current_user):
    cached_report = get_from_cache(current_user.id, "max_tasks_date")

    if cached_report:
        return build_response(success=True, payload={"max_tasks_date": cached_report}, error="")

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

    store_in_cache(current_user.id, "max_tasks_date", max_tasks_date)

    return build_response(success=True, payload={"max_tasks_date": max_tasks_date}, error="")


@token_required
def get_weekly_tasks(current_user):
    cached_report = get_from_cache(current_user.id, "weekday_tasks")

    if cached_report:
        return build_response(success=True, payload=cached_report, error="")

    tasks = Task.query.filter_by(user_id=current_user.id).all()

    if not tasks:
        logger.error("No task found")
        return build_response(success=False, payload="", error="No task found")

    week_days = {'Monday': 0, 'Tuesday': 0, 'Wednesday': 0,
                 'Thursday': 0, 'Friday': 0, 'Saturday': 0, 'Sunday': 0}

    for task in tasks:
        day = task.creation_date.strftime('%A')
        week_days[day] += 1

    store_in_cache(current_user.id, "weekday_tasks", week_days)

    return build_response(success=True, payload=week_days, error="")


@token_required
def get_similar_tasks(current_user):
    cached_report = get_from_cache(current_user.id, "similar_tasks")
    
    if cached_report:
        return build_response(success=True, payload=cached_report, error="")

    tasks = Task.query.filter_by(user_id=current_user.id).all()

    if not tasks:
        logger.error("No task found")
        return build_response(success=False, payload="", error="No task found")

    similar_tasks = []

    if not tasks:
        return build_response(success=False, payload="", error="No task found")

    for task1, task2 in itertools.combinations(tasks, 2):
        if is_same(task1.description, task2.description):
            similar_tasks.append([task1.id, task2.id])

    store_in_cache(current_user.id, "similar_tasks", similar_tasks)

    return build_response(success=True, payload=similar_tasks, error="")
