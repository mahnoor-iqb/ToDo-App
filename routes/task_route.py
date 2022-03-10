
from flask import Blueprint

from controllers.task_controller import show, add

task_bp = Blueprint('task_bp', __name__)
task_bp.route('/', methods=['GET'])(show)
task_bp.route('/', methods=['POST'])(add)