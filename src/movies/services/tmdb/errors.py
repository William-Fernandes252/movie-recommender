class BaseError(Exception):
    message: str
    status: int

    def __init__(self, message: str, status: int):
        """Initialize the error with the message and the status."""
        self.message = message
        status = status
        super().__init__(self.message)


class BadRequestError(BaseError):
    def __init__(self, message: str):
        """Initialize the bad request error with the message."""
        super().__init__(message, 400)
