import datetime
from flask import SQLAlchemy
from src.error_handling.CustomError import CustomError
db = SQLAlchemy()

class Activity(db.Model):
    """Activity represents the status lifetime of a task.

    Attributes:
    status (bool): Represents whether the task is active
    start (None | datetime.datetime): The start of the task's active life (if this has yet to be determined, is None)
    end (None | datetime.datetime): The end of the task's active life (if this has yet to be determined, is None)
    """

    # set up an activity table within our database
    __tablename__ = 'activity'
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.Boolean, nullable=False, default=False)
    start = db.Column(db.DateTime, nullable=True, default=None)
    end = db.Column(db.DateTime, nullable=True, default=None)

    def __init__(self, start=None, end=None):
        """Initialises an Activity where start/end dates are provided

        Args:
            start (datetime.datetime): start date of when the task is active
            end (datetime.datetime): end date of when the task ceases status

        Raises:
            ValueError: start date occurs after end date
            ValueError: start date occurs before current time
        """

        # check if start/end dates are valid:
        # check that start date happens before the end date, if not, swap the two dates
        if start > end:
            new_end = start
            start = end
            end = new_end

        # check that start date occurs on or after the current date
        if start < datetime.datetime.now():
            # start date is invalid, change set start and end to None
            start = None
            end = None

        # provided dates are valid so initialise Activity with start/end
        self.start = start
        self.end = end

        # update the Activity's active status so that active status applies to start/end dates
        self.updateActivity()

    def isActive(self):
        """Returns a boolean representing whether the status is active

        Returns:
            bool: True = status is active, False = status is inactive
        """
        return self.status

    def updateActivity(self):
        """
        Update the status to show if the status is active
        """

        # determine current time
        now = datetime.datetime.now()

        # check if start has been specified
        if self.start is not None:
            # check if the start date of the activity is before or equal to the current date
            if self.start <= now:
                # if the end date of the activity lifetime is unspecified,
                # delete the current start date as an activity cannot activate without an end date
                if self.end is None:
                    self.start = None

                # if the end date is specified; set status to be:
                # True if the end date is before now, otherwise set status to False
                else:
                    self.status = self.end < now
            else:
                self.status = False

        # start is unspecified, so the activity status must be inactive
        else:
            self.status = False

    def changeDates(self, newStart: datetime.datetime, newEnd: datetime.datetime):
        """Change the start and end dates of an status

        Args:
            newStart (datetime.datetime): New start date for the activity
            newEnd (datetime.datetime): New end date for the activity

        Raises:
            CustomError: Activity is active so modification of dates is not possible
            CustomError: The provided start date occurs after the provided end date
            CustomError: Start date provided occurs before the current date
        """
        # Check if modification is possible:
        # if the status is active, raise error
        if self.isActive():
            raise CustomError("Dates cannot be modified in an active environment")
        if self.end > datetime.datetime.now():
            raise CustomError("Dates cannot be modified after the status has ended")
        # if the new start date occurs after the new end date, raise error
        if newStart >= newEnd:
            raise CustomError("Start date must be after the end date")
        # if the new start date occurs before the current date, raise error
        if datetime.datetime.now() <= newStart:
            raise CustomError(
                "invalid start date, start date must be after the current date"
            )

        # provided dates are valid and the status can be modified, so time to modify!
        # update start and end dates
        self.start = newStart
        self.end = newEnd
        # update the status's active status just in case the status is now activated due to the change in start/end dates
        self.updateActivity()
