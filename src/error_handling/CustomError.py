import uuid


class CustomError(Exception):
    def __new__(cls, message):
        if message in message_to_uuid:
            return get_error_by_message(message)
        else:
            return super(CustomError, cls).__new__(cls)

    def __init__(self, message):
        if message not in message_to_uuid:
            self.message = message
            self.ID = uuid.uuid4()
            message_to_uuid[self.message] = self.ID
            error_store[self.ID] = self

    def __str__(self):
        return f"Error {self.ID}: {self.message}"


error_store: dict[uuid, CustomError] = {}
message_to_uuid: dict[str, uuid] = {}


def get_error_by_message(message):
    """
    Retrieves an error which has the provided message
    @param message: The message of the error
    @return CustomError: The error associated with the provided message
    """

    return error_store.get(message_to_uuid[message], None)
