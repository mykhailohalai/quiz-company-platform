from app.exceptions.user_exceptions import (
    UserAlreadyExistsException,
    UserNotFoundException,
)


class FakeUserRepository:
    def __init__(self, users=None):
        self.users = {user.id: user for user in (users or [])}

    async def get_all(self, skip=0, limit=10):
        users = list(self.users.values())
        return users[skip : skip + limit], len(users)

    async def get_all_users(self):
        return list(self.users.values())

    async def get_by_id(self, user_id):
        user = self.users.get(user_id)
        if user is None:
            raise UserNotFoundException(user_id)
        return user

    async def get_by_username(self, username):
        for user in self.users.values():
            if user.username == username:
                return user
        return None

    async def get_by_email(self, email):
        for user in self.users.values():
            if user.email == email:
                return user
        return None

    async def create(self, user):
        for existing in self.users.values():
            if existing.username == user.username:
                raise UserAlreadyExistsException("username")
            if user.email is not None and existing.email == user.email:
                raise UserAlreadyExistsException("email")
        self.users[user.id] = user
        return user

    async def delete(self, user_id):
        if user_id not in self.users:
            raise UserNotFoundException(user_id)
        del self.users[user_id]
        return True

    async def update(self, user_id, updated_user):
        user = self.users.get(user_id)
        if user is None:
            raise UserNotFoundException(user_id)
        for field, value in updated_user.model_dump(exclude_unset=True).items():
            setattr(user, field, value)
        return user
