from flask import Flask
from models.user import db
from flask_migrate import Migrate

from routes.user_route import user_bp
from routes.task_route import task_bp


# init app
app = Flask(__name__)

# init db
app.config.from_object('config')
db.init_app(app)
migrate = Migrate(app, db)

app.register_blueprint(user_bp, url_prefix='/users')
app.register_blueprint(task_bp, url_prefix='/tasks')

@app.route('/')
def home():
    return "<h1>Hello World</h1>"

if __name__== "__main__":
    app.run()
