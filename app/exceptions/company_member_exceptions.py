from uuid import UUID


class CompanyMemberNotFoundException(Exception):
    def __init__(self, user_id: UUID):
        self.user_id = user_id
        super().__init__(f"Company member with id {user_id} was not found.")


class CompanyMemberAlreadyExistsException(Exception):
    def __init__(self, field: str):
        self.field = field
        super().__init__(f"Company member with the same {field} already exists.")


class CompanyMemberNotAdminException(Exception):
    def __init__(self, user_id: UUID):
        self.user_id = user_id
        super().__init__(f"Company member with id {user_id} is not admin.")


class CompanyMemberAdminException(Exception):
    def __init__(self, user_id: UUID):
        self.user_id = user_id
        super().__init__(f"Company member with id {user_id} is admin already.")
