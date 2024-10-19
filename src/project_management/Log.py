from datetime import datetime
from enum import Enum

from src.error_handling.CustomError import CustomError
from src.project_management.Activity import Activity

from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

class LogType(str, Enum):
    ACTIVE = "ActiveLog"
    INACTIVE = "InactiveLog"


class Log(db.Model):

    # set up an activity table within our database
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    type = db.Column(db.Enum(LogType), nullable = False)

    __mapper_args__ = {
        'polymorphic_on': type,        # Polymorphic column
        'polymorphic_identity': 'log'  # Base identity
    }

    def __init__(self, title: str, log_type: LogType):
        self.title = title
        self.type = log_type

    def is_active(self):
        raise CustomError(
            "A LogModel object cannot be checked for Activity, you should be passing a child class of LogModel (ActiveLog and InactiveLog)"
        )

    def is_immutable(self):
        return False


class InactiveLog(Log):
    __mapper_args__ = {
        'polymorphic_identity': LogType.INACTIVE  # Identity for InactiveLog
    }

    def __init__(self, title: str, activity):
        super().__init__(title=title, log_type=LogType.INACTIVE)

    def is_active(self):
        return self.activity.status


class ActiveLog(Log):
    activity_id = db.Column(db.Integer, db.ForeignKey('activity.id'))
    activity = db.relationship("Activity")

    __mapper_args__ = {
        'polymorphic_identity': LogType.ACTIVE  # Identity for ActiveLog
    }

    def __init__(self, title: str, activity: Activity = Activity()):
        super().__init__(title=title, log_type=LogType.ACTIVE)
        self.activity = activity

    def is_active(self):
        return self.activity.status

    def is_immutable(self):
        return datetime.now() > self.activity.end
