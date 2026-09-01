class AppException(Exception):
    def __init__(self, status_code: int, error_code: str, message: str, details=None):
        self.status_code = status_code
        self.error_code = error_code
        self.message = message
        self.details = details

class TaskNotFoundException(AppException):
    def __init__(self, task_id: int):
        super().__init__(
            status_code=404,
            error_code="TASK_NOT_FOUND",
            message=f"Task with ID {task_id} was not found."
        )