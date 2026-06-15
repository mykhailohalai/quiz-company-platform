class ForbiddenException(Exception):
    def __init__(self):
        super().__init__(f"Access denied.")
