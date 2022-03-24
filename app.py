from flask import Flask, request, url_for
from flask_migrate import Migrate
from models.user import db, User
from models.session import Session
from werkzeug.exceptions import HTTPException
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer
import jwt
from datetime import timedelta, datetime
import os

from routes.user_route import user_bp
from routes.task_route import task_bp
from utils.utils import build_response


app = Flask(__name__)
app.config.from_object('config')

db.init_app(app)
migrate = Migrate(app, db)

app.secret_key = os.urandom(32)

mail = Mail(app)
serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])

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

    token = serializer.dumps(email)
    msg = Message("Email Confirmation",
                  sender="testmahnoor@gmail.com", recipients=[email])
    link = url_for('confirm_email', token=token, _external=True)
    msg.body = f"Confirm your email address: {link}"
    mail.send(msg)

    user = User(email=email, password=hashed_password,
                admin=False, activated=False)
    db.session.add(user)
    db.session.commit()

    return build_response(success=True, payload="Confirmation email has been sent. Please confirm your email.", error="")


@app.route('/email-confirmation/<token>', methods=['GET'])
def confirm_email(token):
    try:
        email = serializer.loads(
            token,
            max_age=3600
        )
    except:
        return build_response(success=False, payload="", error="The confirmation link is invalid or has expired.")

    user = User.query.filter_by(email=email).first()

    if user.activated:
        return build_response(success=True, payload="", error="User already activated.")

    user.activated = 1

    db.session.merge(user)
    db.session.commit()
    return build_response(success=True, payload="Email Confirmed!", error="")


@app.route('/login', methods=['POST'])
def login():
    user_email = request.json['email']
    user = User.query.filter_by(email=user_email).first()

    if not user.activated:
        return build_response(success=False, payload="",
                          error="Please verify your email before logging in.")


    password = request.json['password']

    if check_password_hash(user.password, password):
        token = jwt.encode({
            'user_id': user.id,
            'exp': datetime.utcnow() + timedelta(hours=1)
        }, app.config['SECRET_KEY'])

        #Convert token to string
        token = token.decode("utf-8") 

        session = Session(id=token, user_id=user.id)
        db.session.add(session)
        db.session.commit()
        res = build_response(
            success=True, payload="Login Successful!", error="")
        res.set_cookie('access_token', token)
        return res

    return build_response(success=False, payload="",
                          error="Please check your login credentials!")


@app.route('/logout')
def logout():
    token = request.cookies.get('access_token') 

    if not token:
            return build_response(success=False, payload="", error="Access token not provided!")   

    sess = Session.query.filter_by(id=token).first()
    db.session.delete(sess)
    db.session.commit()
    res = build_response(success=True, payload="Logged Out!", error="")
    res.delete_cookie('access_token')

    return res


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
