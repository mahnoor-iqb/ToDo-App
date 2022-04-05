from models.user import User
from models.task import Task
from flask_sqlalchemy import SQLAlchemy
import logging
from flask_mail import Message
from datetime import datetime
from sqlalchemy import func
from app import app
from app import mail


db = SQLAlchemy()


logger = logging.getLogger(__name__)


@app.cli.command()
def send_reminder_email():
    '''
    Send emails to users to inform about tasks scheduled today

    @app.cli.command() creates a custom flask command which is then run as a scheduled cron job:

        0 0 * * * cd /home/emumba/Desktop/ToDo-App && venv/bin/flask send-reminder-email >>scheduled.log 2>&1

    '''
    
    today = datetime.today().strftime('%Y-%m-%d')
    logger.debug(today)
    users = User.query.all()

    for user in users:
        tasks_due = Task.query.filter(Task.user_id == user.id).filter(
            func.DATE(Task.due_date) == today).all()

        if tasks_due:
            message = "Tasks due today: " + \
                " ".join([task.title for task in tasks_due])
            msg = Message("Task Reminders",
                          sender="testmahnoor@gmail.com", recipients=[user.email])

            msg.body = message
            mail.send(msg)
            logger.info("Email sent")
