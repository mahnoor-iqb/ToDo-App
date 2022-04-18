from models.user import User
from models.task import Task
from models.session import Session
from datetime import datetime
from app import app as test_app
from app import db as test_db
import pytest


test_app.config["TESTING"] = True
test_app.testing = True

# This creates an in-memory sqlite db
test_app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite://"


# Add records in DB for testing
with test_app.app_context():
    test_db.create_all()
    user1 = User(email="testuser@gmail.com", password="password")
    user1.activated = True
    test_db.session.add(user1)

    task1 = Task(title="My test task 1", description="This is my test task 1",
                 creation_date=datetime.strptime(
                     "2022-03-20 20:20:40", '%Y-%m-%d %H:%M:%S'),
                 due_date=datetime.strptime(
                     "2022-04-20 21:11:18", '%Y-%m-%d %H:%M:%S'),
                 completion_date=datetime.strptime(
                     "2022-04-19 22:17:22", '%Y-%m-%d %H:%M:%S'),
                 completion_status=1, user_id=1)

    test_db.session.add(task1)
    task2 = Task(title="My test task 2", description="This is my test task 2",
                 creation_date=datetime.strptime(
                     "2022-03-20 20:20:40", '%Y-%m-%d %H:%M:%S'),
                 due_date=datetime.strptime(
                     "2022-04-20 21:11:18", '%Y-%m-%d %H:%M:%S'),
                 completion_date=None, completion_status=0, user_id=1)

    test_db.session.add(task2)
    test_db.session.commit()


@pytest.fixture
def new_user():
    email = "jane.doe@gmail.com"
    password = "ThisIsMyTestPassword."
    user = User(email, password)
    return user


@pytest.fixture
def new_task():
    title = "Test Task"
    description = "This is a test task."
    creation_date = datetime.strptime(
        "2022-02-20 18:11:41", '%Y-%m-%d %H:%M:%S')
    due_date = datetime.strptime(
        "2022-03-20 18:11:41", '%Y-%m-%d %H:%M:%S')
    completion_date = None
    completion_status = 0
    user_id = 5

    task = Task(title=title,
                description=description,
                creation_date=creation_date,
                due_date=due_date,
                completion_date=completion_date,
                completion_status=completion_status,
                user_id=user_id)

    return task


@pytest.fixture
def client():
    client = test_app.test_client()
    yield client
