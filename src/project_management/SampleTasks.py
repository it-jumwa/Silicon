from src.project_management.Log import LogModel
from src.project_management.Task import Task, Priority, Status, Tag

sample_tasks = [
    Task(
        "Task 1",
        LogModel("sample log 1"),
        "a",
        "This is sample task number 1.",
        5,
        Priority.LOW,
        [Status.NOT_STARTED],
        Tag.FRONT_END,
    ),
    Task(
        "Task 2",
        LogModel("sample log 2"),
        "a",
        "This is sample task number 2.",
        4,
        Priority.MEDIUM,
        [Status.IN_PROGRESS_PLANNING],
        Tag.BACK_END,
    ),
    Task(
        "Task 3",
        LogModel("sample log 1"),
        "a",
        "This is sample task number 3.",
        3,
        Priority.IMPORTANT,
        [Status.IN_PROGRESS_INTEGRATION],
        Tag.UI_UX,
    ),
    Task(
        "Task 4",
        LogModel("sample log 2"),
        "b",
        "This is sample task number 4.",
        2,
        Priority.URGENT,
        [Status.IN_PROGRESS_DEVELOPMENT],
        Tag.API,
    ),
    Task(
        "Task 5",
        LogModel("sample log 1"),
        "b",
        "This is sample task number 5.",
        1,
        Priority.IMPORTANT,
        [Status.IN_PROGRESS_TESTING],
        Tag.FRONT_END,
    ),
    Task(
        "Task 6",
        LogModel("sample log 2"),
        "b",
        "This is sample task number 6.",
        1,
        Priority.MEDIUM,
        [Status.COMPLETE],
        Tag.BACK_END,
    ),
]
