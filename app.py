from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from datetime import datetime


# init app
app = Flask(__name__)

# init db
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///todo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

@app.route('/')
def home():
    return "<h1>Hello World</h1>"

if __name__== "__main__":
    app.run(debug=True)
