class NotAdminError(Exception):
    """Exception raised when a user is not an admin."""

    def __init__(self, message: object) -> None:
        super().__init__(message)
        self.message = message
