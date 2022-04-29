from flask import Flask, redirect, request, url_for
from flask_crontab import Crontab
from flask_migrate import Migrate
from models.user import db, User
from models.session import Session
from werkzeug.exceptions import HTTPException
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer
import jwt
from datetime import timedelta, datetime
from google_auth_oauthlib.flow import Flow
import os
import pathlib
from utils.utils import build_response
from pip._vendor import cachecontrol
import google.auth.transport.requests
from google.oauth2 import id_token
import requests
from dotenv import load_dotenv
import logging


# Load environment variables
load_dotenv()


# Configure logger
logging.basicConfig(filename= "logger.log", filemode='w', format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
    datefmt='%Y-%m-%d:%H:%M:%S',
    level=logging.DEBUG)

logger = logging.getLogger(__name__)


app = Flask(__name__)
app.config.from_object('config')

logger.info('App started in %s', os.getcwd())

db.init_app(app)
migrate = Migrate(app, db)

mail = Mail(app)
serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])


# Add a cron job for sending reminder emails
crontab = Crontab(app)
from utils.task_reminders import send_reminders


from routes.user_route import user_bp
from routes.task_route import task_bp
from routes.report_route import report_bp

app.register_blueprint(user_bp, url_prefix='/users')
app.register_blueprint(task_bp, url_prefix='/tasks')
app.register_blueprint(report_bp, url_prefix='/reports')


GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
OAUTHLIB_INSECURE_TRANSPORT = os.getenv("OAUTHLIB_INSECURE_TRANSPORT")

client_secrets_file = os.path.join(
    pathlib.Path(__file__).parent, "client_secret.json")

flow = Flow.from_client_secrets_file(client_secrets_file=client_secrets_file,
                                     scopes=["https://www.googleapis.com/auth/userinfo.profile",
                                             "https://www.googleapis.com/auth/userinfo.email", "openid"],
                                     redirect_uri="http://127.0.0.1:5000/google-login-callback")


@app.route('/login-with-google')
def login_with_google():
    authorization_url = flow.authorization_url()
    return redirect(authorization_url[0])


@app.route('/google-login-callback')
def callback():
    flow.fetch_token(authorization_response=request.url)

    credentials = flow.credentials
    request_session = requests.session()
    cached_session = cachecontrol.CacheControl(request_session)
    token_request = google.auth.transport.requests.Request(
        session=cached_session)

    try:
        account = id_token.verify_oauth2_token(
            id_token=credentials._id_token,
            request=token_request,
            audience=GOOGLE_CLIENT_ID
        )

    except:
        logger.error("Access token verification failed")
        return build_response(success=False, payload="", error="Access token verification failed!")

    oauth_user = User.query.filter_by(oauth=True).filter_by(
        email=account.get("email")).first()

    if not oauth_user:
        user = User.query.filter_by(email=account.get("email")).first()
        if user:
            logger.error("User with provided email already exists in the database")
            return build_response(success=False, payload="", error="User already exists!")

        oauth_user = User(email=account.get("email"),
                          password=None, admin=0, activated=1, oauth=1)
        db.session.add(oauth_user)
        db.session.commit()
        logger.info("New Oauth user added to database")

    # Log in user
    token = jwt.encode({
        'user_id': oauth_user.id,
        'exp': datetime.utcnow() + timedelta(days=1)
    }, app.config['SECRET_KEY'])

    # Convert token to string
    token = token.decode("utf-8")

    session = Session(id=token, user_id=oauth_user.id)
    db.session.add(session)
    db.session.commit()

    res = build_response(success=True, payload="Login Successful!", error="")
    res.set_cookie('access_token', token)
    logger.info("User login successful")
    return res


@app.route('/signup', methods=['POST'])
def register():
    email = request.json.get("email")

    if not email:
        return build_response(success=False, payload="", error="Email not provided!")

    user_exists = User.query.filter_by(email=email).first()

    if user_exists:
        logger.error("User email already exists")
        return build_response(success=False, payload="", error="User email already exists!")

    token = serializer.dumps(email)

    msg = Message("Email Confirmation",
                  sender="testmahnoor@gmail.com", recipients=[email])
    link = url_for('confirm_email', token=token, _external=True)
    msg.body = f"Confirm your email address: {link}"
    mail.send(msg)

    logger.info("Account confirmation email sent")

    user = User(email=email, password= request.json['password'])
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
        logger.error("Email confirmation token is invalid or has expired.")
        return build_response(success=False, payload="", error="The confirmation link is invalid or has expired.")

    user = User.query.filter_by(email=email).first()

    if user.activated:
        logger.error("User already activated")
        return build_response(success=True, payload="", error="User already activated.")

    user.activated = 1

    db.session.merge(user)
    db.session.commit()

    logger.info("User email confirmation successful")
    return build_response(success=True, payload="Email Confirmed!", error="")


@app.route('/login', methods=['POST'])
def login():
    user_email = request.json['email']
    user = User.query.filter_by(email=user_email).first()

    if not user.activated:
        logger.error("User not activated")
        return build_response(success=False, payload="",
                              error="Please verify your email before logging in.")

    password = request.json['password']

    if check_password_hash(user.password, password):
        token = jwt.encode({
            'user_id': user.id,
            'exp': datetime.utcnow() + timedelta(days=1)
        }, app.config['SECRET_KEY'])

        # Convert token to string
        token = token.decode("utf-8")

        session = Session(id=token, user_id=user.id)
        db.session.add(session)
        db.session.commit()
        res = build_response(
            success=True, payload="Login Successful!", error="")
        res.set_cookie('access_token', token)

        logger.info("User login successful")
        return res

    logger.error("Incorrect login credentials")
    return build_response(success=False, payload="",
                          error="Please check your login credentials!")


@app.route('/forgot-password', methods=['POST'])
def forgot_password():
    email = request.json["email"]

    user = User.query.filter_by(email=email).first()

    if not user:
        logger.error("User does not exist")
        return build_response(success=False, payload="", error="User does not exist!")

    if user.oauth:
        logger.error("Permission denied for Oauth user")
        return build_response(success=False, payload="", error="Users logged in with Google can not use this feature!")

    token = serializer.dumps(email)

    msg = Message("Reset Password",
                  sender="testmahnoor@gmail.com", recipients=[email])

    link = url_for('validate_reset_password', token=token, _external=True)
    msg.body = f"Reset Password: {link}"
    mail.send(msg)

    logger.info("Reset password link sent")

    return build_response(success=True, payload="Please follow the link sent to your email address to proceed.", error="")


@app.route('/validate-reset-password/<token>', methods=['GET'])
def validate_reset_password(token):
    try:
        email = serializer.loads(
            token,
            max_age=3600
        )
    except:
        logger.error("The forgot password token is invalid or has expired.")
        return build_response(success=False, payload="", error="The forgot password link is invalid or has expired.")

    user = User.query.filter_by(email=email).first()

    if not user:
        logger.error("User does not exist")
        return build_response(success=False, payload="", error="User doesn't exist")

    logger.info("User verified for password reset")
    return build_response(success=True, payload="Verified!", error="")


@app.route('/reset-password/<token>', methods=['POST'])
def reset_password(token):
    try:
        email = serializer.loads(
            token,
            max_age=3600
        )
    except:
        logger.error("The forgot password link is invalid or has expired.")
        return build_response(success=False, payload="", error="The forgot password link is invalid or has expired.")

    user = User.query.filter_by(email=email).first()

    hashed_password = generate_password_hash(request.json['password'], method='sha256')
    user.password = hashed_password
    db.session.merge(user)
    db.session.commit()

    logger.info("Password reset successful")
    return build_response(success=True, payload="Password reset successful!", error="")


@app.route('/logout')
def logout():
    token = request.cookies.get('access_token')

    if not token:
        logger.error("Access token not provided")
        return build_response(success=False, payload="", error="Access token not provided!")

    sess = Session.query.filter_by(id=token).first()
    db.session.delete(sess)
    db.session.commit()
    res = build_response(success=True, payload="Logged Out!", error="")
    res.delete_cookie('access_token')
    logger.info("Log out successful")
    return res


@app.errorhandler(404)
def page_not_found(e):
    logger.error(e.description)
    return build_response(success=False, payload={}, error=e.description)


@app.errorhandler(HTTPException)
def handle_exception(e):
    logger.error(e.description)
    return build_response(success=False, payload={}, error=e.description)


@app.route('/')
def home():
    return "<a href='/login-with-google'><button>Login With Google</button></a>"


if __name__ == "__main__":
    app.debug = True
    app.run()
