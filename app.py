from flask import Flask, session, request
from flask_session import Session
from flask_migrate import Migrate
from flask_login import LoginManager, login_user, logout_user, login_required
from models.user import db, User
from werkzeug.exceptions import HTTPException
from werkzeug.security import generate_password_hash, check_password_hash
import os

from routes.user_route import user_bp
from routes.task_route import task_bp
from utils.utils import build_response



app = Flask(__name__)
app.config.from_object('config')

db.init_app(app)
migrate = Migrate(app, db)

Session(app)
app.secret_key = os.urandom(32)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)


@login_manager.user_loader
def load_user(id):
    return User.query.get(id)


app.register_blueprint(user_bp, url_prefix='/users')
app.register_blueprint(task_bp, url_prefix='/tasks')


@app.route('/signup', methods=['POST'])
def register():
    email = request.json["email"]

    user_exists = User.query.filter_by(email=email).first()

    if user_exists:
        return build_response(success=False, payload="", error="User email already exists!")

    hashed_password = generate_password_hash(
        request.json['password'], method='sha256')

    user = User(email=email, password=hashed_password, admin=False, email_activated = False)
    db.session.add(user)
    db.session.commit()

    return build_response(success=True, payload="Sign up Successful!", error="")


@app.route('/login', methods=['POST'])
def login():
    user_email = request.json['email']
    user = User.query.filter_by(email=user_email).first()

    password = request.json['password']

    if check_password_hash(user.password, password):
        session["user"] = user.id
        login_user(user)
        return build_response(success=True, payload="Login Successful!", error="")

    return build_response(success=False, payload="",
                          error="Please check your login credentials!")


@app.route('/logout')
@login_required
def logout():
    session.pop('user', None)
    logout_user()
    return build_response(success=True, payload="Logged Out!", error="")


@app.errorhandler(404)
def page_not_found(e):
    return build_response(success=False, payload={}, error=e.description)


@app.errorhandler(HTTPException)
def handle_exception(e):
    return build_response(success=False, payload={}, error=e.description)


@app.route('/')
def home():
    return build_response(success=True, payload="Welcome to Todo App", error="")


if __name__ == "__main__":
    app.run()
