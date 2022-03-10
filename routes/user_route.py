from flask import Blueprint

from controllers.user_controller import show, add

user_bp = Blueprint('user_bp', __name__)
user_bp.route('/', methods=['GET'])(show)
user_bp.route('/', methods=['POST'])(add)
