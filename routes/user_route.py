from flask import Blueprint

from controllers.user_controller import show_all, add, show

user_bp = Blueprint('user_bp', __name__)
user_bp.route('/', methods=['GET'])(show_all)
user_bp.route('/', methods=['POST'])(add)
user_bp.route('/<int:user_id>', methods=['GET'])(show)
