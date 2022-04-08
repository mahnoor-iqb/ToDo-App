from flask import Blueprint

from controllers.report_controller import count_tasks, get_average_tasks, get_late_tasks, get_max_tasks_date, get_weekly_tasks, get_similar_tasks

report_bp = Blueprint('report_bp', __name__)
report_bp.route('/task-count', methods=['GET'])(count_tasks)
report_bp.route('/average-tasks', methods=['GET'])(get_average_tasks)
report_bp.route('/late-tasks', methods=['GET'])(get_late_tasks)
report_bp.route('/max-tasks-date', methods=['GET'])(get_max_tasks_date)
report_bp.route('/weekly-tasks', methods=['GET'])(get_weekly_tasks)
report_bp.route('/similar-tasks', methods=['GET'])(get_similar_tasks)
