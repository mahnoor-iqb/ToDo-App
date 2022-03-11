
from flask import Blueprint

from controllers.task_controller import show_all, add, delete,update, show

task_bp = Blueprint('task_bp', __name__)
task_bp.route('/', methods=['GET'])(show_all)
task_bp.route('/', methods=['POST'])(add)
task_bp.route('/<int:task_id>', methods=['GET'])(show)
task_bp.route('/<int:task_id>', methods=['DELETE'])(delete)
task_bp.route('/<int:task_id>', methods=['PUT'])(update)