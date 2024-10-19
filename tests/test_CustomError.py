from src.error_handling.CustomError import (
    CustomError,
    message_to_uuid,
    error_store,
    get_error_by_message,
)


def test_custom_errors():
    """
    Runs all the test functions related to CustomError creation and retrieval.
    """
    test_creating_errors()


def test_creating_errors():
    """
    Tests the creation of errors and checks whether they are stored and retrieved properly.
    """
    # Define some test messages
    message1 = "error 1"
    message2 = "error 2"
    message3 = "error 3"
    message2_duplicate = "error 2"

    # Create error objects
    error1 = CustomError(message1)
    error2 = CustomError(message2)
    error3 = CustomError(message3)
    error2duplicate = CustomError(message2_duplicate)

    # Run checks
    print("CHECK ERRORS HAVE BEEN CREATED CORRECTLY")
    test_error_initialization(error1, error2, error3, error2duplicate)
    test_get_error_by_uuid(error1.ID, error2.ID, error3.ID, error2duplicate.ID)
    test_get_error_by_message(
        [
            (error1, message1),
            (error2, message2),
            (error3, message3),
            (error2duplicate, message2_duplicate),
        ]
    )


def test_error_initialization(error1, error2, error3, error2duplicate):
    """
    Checks whether errors are initialized correctly and stored as expected.
    """
    print("\n--- ERROR INITIALIZATION TESTS ---")

    # Check each error's initialization
    for i, (error, message) in enumerate(
            [
                (error1, "error 1"),
                (error2, "error 2"),
                (error3, "error 3"),
                (error2duplicate, "error 2"),
            ],
            1,
    ):
        print(f"Check error{i}:")
        print(f"- Correct error message: {error.message == message}")
        print(f"- Error in error_store: {get_error_by_message(error.message) == error}")
        print(f"Error ID: {error.ID}\n")

    # Check store sizes
    print(f"Check message_to_uuid length: {len(message_to_uuid)} (should be 3)")
    print(f"Check error_store length: {len(error_store)} (should be 3)\n")

    # Check that the duplicate error shares the same ID
    print(f"Check that error2 == error2duplicate: {error2 == error2duplicate}\n")


def test_get_error_by_uuid(id1, id2, id3, id2dup):
    """
    Checks whether errors can be retrieved by their unique UUID.
    """
    print("\n--- ERROR RETRIEVAL BY UUID TESTS ---")
    print(f"Error 1 is in error_store: {id1 in error_store}")
    print(f"Error 2 is in error_store: {id2 in error_store}")
    print(f"Error 3 is in error_store: {id3 in error_store}")
    print(f"Error 2 duplicate is in error_store: {id2dup in error_store}")

    print(f"Check error IDs are unique: {len({id1, id2, id3}) == 3}")
    print(f"Error 2 shares its ID with error2duplicate: {id2 == id2dup}\n")


def test_get_error_by_message(errors_with_messages):
    """
    Checks whether errors can be retrieved by their associated messages.
    """
    print("\n--- ERROR RETRIEVAL BY MESSAGE TESTS ---")
    for i, (error, message) in enumerate(errors_with_messages, 1):
        if i == 4:
            i = "2 duplicate"
        print(
            f"Check error {i}: Retrieved error matches original: {get_error_by_message(message) == error}"
        )

    # Check that error2 and error 2duplicate are the same
    error2, message2 = errors_with_messages[1]
    error2dup, _ = errors_with_messages[3]
    print(
        f"Check that error2 and error2duplicate access the same instance: {error2 == error2dup}\n"
    )
