from models.user import User
from models.task import Task
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Message
from datetime import datetime
from sqlalchemy import func
from app import app
from app import mail
from collections import defaultdict
from app import crontab


db = SQLAlchemy()


@crontab.job(minute="0", hour="0")
def send_reminders():
    today = datetime.today().strftime('%Y-%m-%d')
    tasks_due = db.session.query(User, Task).join(
        User).filter(func.DATE(Task.due_date) == today).all()

    if tasks_due:
        groupby_user = defaultdict(list)

        for row in tasks_due:
            groupby_user[row[0]].append(row[1])

        for user, tasks in groupby_user.items():
            send_email(user, tasks)


def send_email(user, tasks):
    message = "Tasks due today:<br>" + \
        "<br>".join(["- "+task.title for task in tasks])

    msg = Message("Task Reminders",
                  sender="testmahnoor@gmail.com", recipients=[user.email])

    msg.body = message
    mail.send(msg)
