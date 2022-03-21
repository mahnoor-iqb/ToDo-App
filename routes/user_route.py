from flask import Blueprint

from controllers.user_controller import show_all_users, show_user, delete_user, update_user

user_bp = Blueprint('user_bp', __name__)
user_bp.route('/', methods=['GET'])(show_all_users)
user_bp.route('/<int:user_id>', methods=['GET'])(show_user)
user_bp.route('/<int:user_id>', methods=['DELETE'])(delete_user)
user_bp.route('/', methods=['PUT'])(update_user)
