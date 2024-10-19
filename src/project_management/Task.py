from enum import Enum

from src.error_handling.CustomError import CustomError
from src.project_management.Log import LogModel

SP_MINIMUM = 1
SP_MAXIMUM = 10


class Tag(Enum):
    """
    Tag is an enumeration for tags, possible tags include; front-end, back-end, UI/UX and API.
    The value of a Tag is a tuple where;
        Tag[0] is a unique int representing a specific tag
        Tag[1] is a string which describes the tag
    """

    FRONT_END = (0, "Front-end")
    BACK_END = (1, "Back-end")
    UI_UX = (2, "UI/UX")
    API = (3, "API")

    """ 
    Provides a description for the tag
    """

    def __str__(self):
        return self.value[1]


class Priority(Enum):
    """
    Priority is an enumeration for degrees of priority. Current priorities include; low, medium, important and urgent.
    The value of a priority is a unique int representing degree of importance (higher values indicate increasing urgency)
    """

    # should we have an unknown/unspecified priority? eg:
    UNSPECIFIED = 0
    LOW = 1
    MEDIUM = 2
    IMPORTANT = 3
    URGENT = 4

    """
    Provides a string describing the priority
    """

    def __str__(self):
        return self.name.replace("_", " ").title()


class Status(Enum):
    """
    Status is an enumeration used to represent the current status of a task
    The value of a Status is a tuple (int, string) where;
        Status[0] is a unique int representing the degree of completeness (higher being closer to completion)
        Status[1] is a string which describes the status
    """

    NOT_STARTED = (1, "Not Started")
    IN_PROGRESS_PLANNING = (2.1, "In-progress: Planning")
    IN_PROGRESS_INTEGRATION = (2.2, "In-progress: Integration")
    IN_PROGRESS_DEVELOPMENT = (2.3, "In-progress: Development")
    IN_PROGRESS_TESTING = (2.4, "In-progress: Testing")
    COMPLETE = (3, "Complete")

    """
    Provides a string describing the status
    """

    def __str__(self):
        return self.value[2]


class Task:
    """Represents a Task within our system"""

    _fields = [
        "title",
        "location",
        "description",
        "storyPoint",
        "priority",
        "status",
        "tags",
        "history",
        "modifier",
    ]
    _fields_inputs = {
        "title": [str],
        "location": [LogModel],
        "description": [str],
        "storyPoint": [int, float],
        "priority": [Priority],
        "status": [Status],
        "tags": [Tag],
        "history": [str],
        "modifier": [str],
    }

    # TODO: can a user modify history?? (like could they potentially delete a comment in the task's history?)
    def __init__(
            self,
            title: str,
            location: LogModel,
            user: str,
            description: str = "",
            storyPoint: float | None = None,
            priority: Priority = Priority.UNSPECIFIED,
            status: Status = Status.NOT_STARTED,
            tags: list[Tag] = [],
    ):
        """Creates a new task

        Args:
            title (str): Title of the task
            location (LogModel): Log the task is in
            user (str): The initial user who created the task
            description (str): Description of the task
            storyPoint (float): Story point estimate for the task
            priority (Priority): Priority of the task
            status (Status): Current status of the task
            tags (Tag): Tag of the task

        Raises:
            AttributeError: Description is over 1000 chars
        """
        if len(description) > 1000:
            raise CustomError("Description for cannot be over 1000 characters")
            # TODO: Discussion: What happens if this error is raised during run time? Will we need to implement some
            #  sort of try except "loop"
        if title == "":
            raise CustomError("Title is empty")

        self.title = title
        self.location = location
        self.description = description
        self.storyPoint = storyPoint
        self.status = status
        self.tags = tags
        self.priority = priority
        self.modifier = None
        self.history = [
            f"{user} created the task {title}",
        ]

    def __str__(self):
        """Provides a string representation of the task

        Returns:
            str: A formatted string representing the task
        """
        return (
            f"Title: {self.title}\n"
            f"Description: {self.desc}\n"
            f"Story point value: {self.storyPoint}\n"
            f"Priority: {self.priority}\n"
            f"Status: {self.status}\n"
            f"Task tag: {self.tags}"
        )

    def _change_field(self, key, value):
        # no need to add to the task's history if we're changing the modifier
        if key == "modifier":
            super().__setattr__(key, value)
        else:
            # check that there is a modifier set so that we can record who made the change
            if self.modifier is None:
                raise CustomError(
                    "Need to set the user who is performing the modifications"
                )
            else:
                # check that value is different from the attribute's current value (no need to record/implement the change in this case)
                if value == self.__getattribute__(key):
                    # TODO: should we raise an error here? check front end implementation
                    pass
                else:
                    # add change to the history log
                    self.history.append(
                        f"{self.modifier} changed the task's {key} to {value}"
                    )
                    # update attribute to have new value
                    super().__setattr__(key, value)

    def __setattr__(self, key, value):
        # check if the key is a key within Task which exists and can be modified within task
        if key not in Task._fields:
            raise CustomError(
                f"Invalid field: {key}\nCannot modify a field which does not apply to task"
            )

        else:
            # check if the user has provided the correct type of input
            for field, field_types in Task._fields_inputs:
                valid_input_type = False
                for field_type in field_types:
                    if isinstance(value, field_type):
                        valid_input_type = True
                        break
                if not valid_input_type:
                    raise CustomError(
                        f"{key} takes inputs of type {field_types}, you provided an invalid input of type {type(value)}"
                    )

            # check if description can be modified to value
            if key == "description":
                # if the user is trying to modify the description and that in this case the user has provided a valid input (<=1000 chars) raise an error
                if len(value) <= 1000:
                    raise CustomError("Description for cannot be over 1000 characters")

            # check if title can be modified to value
            if key == "title":
                pass

            # validate inputs for storyPoint
            elif key == "storyPoint":
                # raise an error if the input is not between the minimum and maximum values of story point
                if not (value >= SP_MINIMUM and SP_MAXIMUM <= 10):
                    raise CustomError(
                        f"Story Point value must be between {SP_MINIMUM} and {SP_MAXIMUM}"
                    )

            # validate inputs for potential update to priority
            elif key == "priority":
                # can priority be changed during an active sprint? NO
                pass

            # validate inputs for potential update to status
            elif key == "status":
                # check if the task is in an inactive sprint and thus status cannot be modified
                if not self.location.is_active():
                    raise CustomError(
                        "Task status can only be updated when the task is in an active sprint"
                    )

            # validate inputs for potential update to tags
            elif key == "tags":
                # TODO: talk with front-end about what functionality they would like. eg: if they want to add/remove tags by sending the modifier a tag and making the modifier change it fom 0 to 1 or 1 to 0, provide me with a list of the new tags, etc.
                print("unable to modify tags at this point in time... ")
                pass

            # validate inputs for potential update to history
            elif key == "history":
                # TODO: check if history can be modified. If so, are there any conditions/limitations to the modification
                print("unable to modify history at this point in time... ")
                pass

            # validate inputs for potential update to modifier
            elif key == "modifier":
                pass

            # validate inputs for potential update to location
            elif key == "location":
                # cannot relocate task if the task is in an active log
                if self.location.is_active():
                    raise CustomError(
                        "Task location can only be updated when the task is in an inactive location"
                    )

                # cannot relocate task to a currently active log
                if value.is_active():
                    raise CustomError(
                        "The provided location log is active, task cannot be moved to an active log"
                    )

                # check if the requested log can accept new tasks to add to it
                if value.is_immutable():
                    raise CustomError(
                        "The provided location log is immutable, meaning the log is no longer allowing modifications"
                    )

                # tasks which are COMPLETE should never be relocated
                if self.status == Status.COMPLETE:
                    raise CustomError(
                        "task is complete. Tasks which are complete cannot be moved."
                    )

            # modify the key, value
            self._change_field(key, value)
