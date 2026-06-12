from app.models.user import User
from app.repositories.base_repository import BaseRepository
from app.schemas.user import UserUpdateRequestSchema
from app.exceptions.user_exceptions import (
    UserNotFoundException,
    UserAlreadyExistsException,
)


class UserRepository(BaseRepository[User, UserUpdateRequestSchema]):
    model = User
    not_found_exception = UserNotFoundException
    already_exists_exception = UserAlreadyExistsException
