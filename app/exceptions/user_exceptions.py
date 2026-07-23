from uuid import UUID

class UserNotFoundException(Exception):
    def __init__(self, user_id: UUID):
        self.user_id = user_id
        super().__init__(f"User with id {user_id} was not found")


class UserAlreadyExistsException(Exception):
    def __init__(self, field: str):
        self.field = field
        super().__init__(f"User with the same {field} already exists")


class InvalidCredentialsException(Exception):
    def __init__(self):
        super().__init__("Invalid username or password")
