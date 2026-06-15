from uuid import UUID


class CompanyNotFoundException(Exception):
    def __init__(self, user_id: UUID):
        self.user_id = user_id
        super().__init__(f"Company with id {user_id} was not found.")


class CompanyAlreadyExistsException(Exception):
    def __init__(self, field: str):
        self.field = field
        super().__init__(f"Company with the same {field} already exists.")
