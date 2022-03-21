
from flask import Blueprint

from controllers.task_controller import show_all_tasks, add_task, delete_task, update_task, show_task, attach_file, download_file

task_bp = Blueprint('task_bp', __name__)
task_bp.route('/', methods=['GET'])(show_all_tasks)
task_bp.route('/', methods=['POST'])(add_task)
task_bp.route('/<int:task_id>', methods=['GET'])(show_task)
task_bp.route('/<int:task_id>', methods=['DELETE'])(delete_task)
task_bp.route('/<int:task_id>', methods=['PUT'])(update_task)
task_bp.route('/<int:task_id>/files', methods=['PATCH'])(attach_file)
task_bp.route('/<int:task_id>/files', methods=['GET'])(download_file)